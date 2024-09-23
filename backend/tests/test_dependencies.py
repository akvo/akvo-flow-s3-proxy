from app.dependencies import bucket_factory
from app.s3 import S3Bucket


def test_bucket_factory():
    factory = bucket_factory()
    bucket = factory("bucket", "fake-id", "fake-secret-key")
    assert isinstance(bucket, S3Bucket)
