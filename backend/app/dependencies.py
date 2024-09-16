from collections.abc import Callable

from app.s3 import S3Bucket


def make_bucket(bucket: str, access_key_id: str, secret_access_key: str) -> S3Bucket:
    return S3Bucket(bucket, access_key_id, secret_access_key)


def bucket_factory() -> Callable[[str, str, str], S3Bucket]:
    return make_bucket
