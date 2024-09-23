from app.dependencies import provide_make_bucket, provide_make_form_validator
from app.flow_config import AWS_ACCESS_ID, AWS_BUCKET, AWS_SECRET, GCP_CREDENTIAL
from app.form_validator import FormValidator
from app.s3 import S3Bucket


def test_bucket_factory():
    factory = provide_make_bucket()
    config = {AWS_BUCKET: "bucket", AWS_ACCESS_ID: "fake-id", AWS_SECRET: "fake-secret"}
    bucket = factory(config)
    assert isinstance(bucket, S3Bucket)


def test_form_validator_factory():
    factory = provide_make_form_validator()
    config = {GCP_CREDENTIAL: "fake-credential"}
    validator = factory(config)
    assert isinstance(validator, FormValidator)
