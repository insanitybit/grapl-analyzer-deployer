#!/usr/bin/env bash
docker build -t my-lambda .
ID=$(docker create my-lambda /bin/true)		# create a container from the image
docker cp $ID:/ ./		# copy the file from the /
mv ./lambda.zip ./analyzer_deployer.zip
cp ./analyzer_deployer.zip ./analyzer-deployer-cdk/
rm -rf ./dev/
rm -rf ./etc/
rm -rf ./proc/
rm -rf ./sys/
rm ./analyzer_deployer.zip
date
