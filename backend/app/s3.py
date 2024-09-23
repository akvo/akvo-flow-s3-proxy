from typing import Any, BinaryIO

import boto3


class S3Bucket:
    def __init__(self, bucket: str, access_key_id: str, secret_access_key: str):
        self.bucket = bucket
        self.client = boto3.client(
            "s3",
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
        )

    def upload(
        self, fileobj: BinaryIO, key: str, extra: dict[str, Any] | None = None
    ) -> None:
        self.client.upload_fileobj(fileobj, self.bucket, key, ExtraArgs=extra)

    def download(self, key: str):  # type: ignore
        return self.client.get_object(Bucket=self.bucket, Key=key)
