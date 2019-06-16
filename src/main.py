import boto3
from botocore.client import BaseClient
from github import Github

from base64 import b64decode

import os


def main():
    # access_token = os.environ['GITHUB_ACCESS_TOKEN']
    # repo_name = os.environ['ANALYZERS_REPOSITORY_NAME']


    access_token = "f260be81d6e7708cf862fbb086ab546d4cd7f318"
    repo_name = 'insanitybit/grapl-analyzers'
    g = Github(access_token)
    s3_client = boto3.client('s3')

    repo = g.get_repo(repo_name)
    print(repo.name)

    analyzer_folders = repo.get_contents("analyzers")
    main_paths = []
    for analyzer_folder in analyzer_folders:
        # print(analyzer_folder)
        main_path = [path for path in repo.get_contents(analyzer_folder.path) if 'main.py' in path.path][0]
        main_paths.append(main_path)
        break

    for main_path in main_paths:
        analyzer_name = main_path.path.split('analyzers/')[1].split('/main.py')[0]
        analyzer_contents = b64decode(main_path.content).decode()

        upload_analyzer(s3_client, analyzer_name, analyzer_contents)
        print(analyzer_name)


def upload_analyzer(s3_client: BaseClient, name: str, contents: str) -> None:
    analyzer_bucket = os.environ['BUCKET_PREFIX'] + '-analyzers-bucket'

    s3_client.put_object(
        Body=contents,
        Bucket=analyzer_bucket,
        Key=f'analyzers/{name}/main.py'
    )


if __name__ == '__main__':
    main()