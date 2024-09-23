from collections.abc import Callable

from app.flow_config import AWS_ACCESS_ID, AWS_BUCKET, AWS_SECRET, GCP_CREDENTIAL
from app.form_validator import FormValidator
from app.s3 import S3Bucket


def make_bucket(config: dict[str, str]) -> S3Bucket:
    return S3Bucket(
        config.get(AWS_BUCKET, ""),
        config.get(AWS_ACCESS_ID, ""),
        config.get(AWS_SECRET, ""),
    )


def provide_make_bucket() -> Callable[[dict[str, str]], S3Bucket]:
    return make_bucket


def make_form_validator(config: dict[str, str]) -> FormValidator:
    return FormValidator(config.get(GCP_CREDENTIAL, ""))


def provide_make_form_validator() -> Callable[[dict[str, str]], FormValidator]:
    return make_form_validator
