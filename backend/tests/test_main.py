import io
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from app.dependencies import provide_make_bucket, provide_make_form_validator
from app.form_validator import FormValidator
from app.main import app
from app.s3 import S3Bucket

client = TestClient(app)


@pytest.fixture
def fake_bucket():
    fake_bucket = Mock(spec=S3Bucket)
    app.dependency_overrides[provide_make_bucket] = lambda: lambda *_: fake_bucket
    yield fake_bucket
    del app.dependency_overrides[provide_make_bucket]


@pytest.fixture
def fake_validator():
    fake_validator = Mock(spec=FormValidator)
    app.dependency_overrides[provide_make_form_validator] = (
        lambda: lambda *_: fake_validator
    )
    yield fake_validator
    del app.dependency_overrides[provide_make_form_validator]


def test_healtz():
    response = client.get("/healtz")
    assert 200 == response.status_code
    assert {"status": "success", "message": "OK!"} == response.json()


def test_put_devicezip_should_call_bucket_upload(fake_bucket, fake_validator):
    fake_config = {"content": "not important"}
    file_name = "test.txt"
    file_content = io.BytesIO(b"<file content>")
    file_content_type = "text/plain"
    with patch("app.main.get_config", return_value=fake_config):
        fake_validator.validate.return_value = True
        client.put(
            f"/instance1/devicezip/123/{file_name}",
            files={"file": (file_name, file_content, file_content_type)},
        )

        fake_validator.validate.assert_called_with(123)
        fake_bucket.upload.assert_called()
        (_first_arg, second_arg, third_arg), _kwargs = fake_bucket.upload.call_args
        assert second_arg == f"devicezip/{file_name}"
        assert third_arg == {"ContentType": file_content_type}


def test_put_devicezip_with_invalid_instance_returns_404(fake_bucket):
    fake_config = {}
    with patch("app.main.get_config", return_value=fake_config):
        response = client.put(
            "/instance1/devicezip/123/test.txt",
            files={"file": io.BytesIO(b"<file content>")},
        )

        assert response.status_code == 404
        fake_bucket.upload.assert_not_called()


def test_put_images_should_call_bucket_upload(fake_bucket, fake_validator):
    fake_config = {"content": "not important"}
    file_name = "test.jpg"
    file_content = io.BytesIO(b"<file content>")
    file_content_type = "image/jpg"
    with patch("app.main.get_config", return_value=fake_config):
        fake_validator.validate.return_value = True
        client.put(
            f"/instance1/images/123/{file_name}",
            files={"file": (file_name, file_content, file_content_type)},
        )

        fake_validator.validate.assert_called_with(123)
        fake_bucket.upload.assert_called()
        (_first_arg, second_arg, third_arg), _kwargs = fake_bucket.upload.call_args
        assert second_arg == f"images/{file_name}"
        assert third_arg == {"ContentType": file_content_type, "ACL": "public-read"}


def test_put_images_with_invalid_instance_returns_404(fake_bucket):
    fake_config = {}
    with patch("app.main.get_config", return_value=fake_config):
        response = client.put(
            "/instance1/images/123/test.jpg",
            files={"file": io.BytesIO(b"<file content>")},
        )

        assert response.status_code == 404
        fake_bucket.upload.assert_not_called()


def test_get_survey_form_should_call_bucket_download(fake_bucket, fake_validator):
    fake_config = {"content": "not important"}
    with patch("app.main.get_config", return_value=fake_config):
        fake_validator.validate.return_value = True
        client.get("/instance1/surveys/123.zip")

        fake_validator.validate.assert_called_with(123)
        fake_bucket.download.assert_called_with("surveys/123.zip")


def test_get_survey_form_with_version_should_call_bucket_download(
    fake_bucket, fake_validator
):
    fake_config = {"content": "not important"}
    with patch("app.main.get_config", return_value=fake_config):
        fake_validator.validate.return_value = True
        client.get("/instance1/surveys/1234567890v12.0.zip")

        fake_validator.validate.assert_called_with(1234567890)
        fake_bucket.download.assert_called_with("surveys/1234567890v12.0.zip")


def test_get_survey_form_with_invalid_instance_returns_404(fake_bucket):
    fake_config = {}
    with patch("app.main.get_config", return_value=fake_config):
        response = client.get("/instance1/surveys/123.zip")

        assert response.status_code == 404
        fake_bucket.download.assert_not_called()


def test_get_survey_form_with_invalid_form_id_returns_404(fake_bucket, fake_validator):
    fake_config = {"content": "not important"}
    with patch("app.main.get_config", return_value=fake_config):
        fake_validator.validate.return_value = False
        response = client.get("/instance1/surveys/123.zip")

        fake_validator.validate.assert_called_with(123)
        assert response.status_code == 404
        fake_bucket.download.assert_not_called()


def test_get_image_should_call_bucket_download(fake_bucket):
    fake_config = {"content": "not important"}
    with patch("app.main.get_config", return_value=fake_config):
        client.get("/instance1/images/file.jpg")
        fake_bucket.download.assert_called_with("images/file.jpg")


def test_get_image_with_invalid_instance_returns_404(fake_bucket):
    fake_config = {}
    with patch("app.main.get_config", return_value=fake_config):
        response = client.get("/instance1/images/file.jpg")

        assert response.status_code == 404
        fake_bucket.download.assert_not_called()


def test_get_refresh():
    with patch("app.main.refresh") as mocked_refresh:
        response = client.get("/refresh")

        assert response.status_code == 200
        mocked_refresh.assert_called_once()


def test_post_refresh():
    with patch("app.main.refresh") as mocked_refresh:
        response = client.post("/refresh")

        assert response.status_code == 200
        mocked_refresh.assert_called_once()
