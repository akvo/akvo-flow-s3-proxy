import io
from unittest.mock import Mock, patch

from app.s3 import S3Bucket


def test_upload():
    fake_client = Mock()
    with patch("app.s3.boto3.client", return_value=fake_client):
        bucket_name = "fake_bucket"
        filename = "test.txt"
        fake_file = io.BytesIO()
        fake_file.write(b"test")

        bucket = S3Bucket(bucket_name, "fake-id", "fake-secret-key")
        bucket.upload(fake_file, filename)

        fake_client.upload_fileobj.assert_called_with(
            fake_file, bucket_name, filename, ExtraArgs=None
        )


def test_download():
    fake_client = Mock()
    with patch("app.s3.boto3.client", return_value=fake_client):
        bucket_name = "fake_bucket"
        filename = "test.txt"

        bucket = S3Bucket(bucket_name, "fake-id", "fake-secret-key")
        bucket.download(filename)

        fake_client.get_object.assert_called_with(Bucket=bucket_name, Key=filename)
