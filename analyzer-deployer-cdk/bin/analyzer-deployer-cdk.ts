#!/usr/bin/env node
import 'source-map-support/register';
import cdk = require('@aws-cdk/cdk');

import apigw = require('@aws-cdk/aws-apigateway');
import lambda = require("@aws-cdk/aws-lambda");
import {Runtime} from "@aws-cdk/aws-lambda";
import s3 = require("@aws-cdk/aws-s3");

const env = require('node-env-file');


class DeployerLambda extends cdk.Stack {
    event_handler: lambda.Function;

    constructor(parent: cdk.App,
                id: string,
    ) {
        super(parent, id + '-stack');

        const bucket = s3.Bucket.fromBucketName(
            this,
            'analyzer-bucket',
            `${process.env.BUCKET_PREFIX}-analyzers-bucket`
        );

        this.event_handler = new lambda.Function(
            this, `${id}-handler`, {
                runtime: Runtime.Python37,
                handler: `main.lambda_handler`,
                code: lambda.Code.asset(`./analyzer_deployer.zip`),
                // vpc: vpc,
                environment: {
                    "GITHUB_SHARED_SECRET": process.env.GITHUB_SHARED_SECRET,
                    "GITHUB_ACCESS_TOKEN": process.env.GITHUB_ACCESS_TOKEN,
                    "GITHUB_REPOSITORY_NAME": process.env.GITHUB_REPOSITORY_NAME,
                    "BUCKET_PREFIX": process.env.BUCKET_PREFIX
                },
                timeout: 25,
                memorySize: 256,
            }
        );

        new apigw.LambdaRestApi(this, id, {
            handler: this.event_handler,
        });
        bucket.grantWrite(this.event_handler);
    }
}


class GraplAnalyzerDeployer extends cdk.App {
    constructor() {
        super();

        env(__dirname + '/.env');

        new DeployerLambda(
            this,
            'grapl-deployer-lambda',
        );

    }
}

new GraplAnalyzerDeployer().run();