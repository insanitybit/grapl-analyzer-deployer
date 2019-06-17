import hmac
from hashlib import sha1

import boto3
from botocore.client import BaseClient
from github import Github

from base64 import b64decode

import os


def verify_payload(payload_body, key, signature):
    new_signature = "sha1=" + hmac.new(key, payload_body, sha1).hexdigest()
    return new_signature == signature


def lambda_handler(event, context):
    shared_secret = os.environ["GITHUB_SHARED_SECRET"]
    access_token = os.environ["GITHUB_ACCESS_TOKEN"]
    repo_name = os.environ["GITHUB_REPOSITORY_NAME"]

    signature = event['headers']["X-Hub-Signature"]

    assert verify_payload(event["body"].encode('utf8'), shared_secret.encode(), signature)

    g = Github(access_token)
    s3_client = boto3.client("s3")

    repo = g.get_repo(repo_name)
    print(repo.name)

    analyzer_folders = repo.get_contents("analyzers")
    main_paths = []
    for analyzer_folder in analyzer_folders:
        # print(analyzer_folder)
        main_path = None

        for path in repo.get_contents(analyzer_folder.path):
            if "main.py" in path.path:
                main_path = path
                break

        if not main_path:
            print("Failed to get main path")
            continue

        main_paths.append(main_path)

    for main_path in main_paths:
        analyzer_name = main_path.path.split("analyzers/")[1].split("/main.py")[0]
        analyzer_contents = b64decode(main_path.content).decode()

        print(f"Uploading {analyzer_name}")
        upload_analyzer(s3_client, analyzer_name, analyzer_contents)


def upload_analyzer(s3_client: BaseClient, name: str, contents: str) -> None:
    analyzer_bucket = os.environ["BUCKET_PREFIX"] + "-analyzers-bucket"

    s3_client.put_object(
        Body=contents, Bucket=analyzer_bucket, Key=f"analyzers/{name}/main.py"
    )
