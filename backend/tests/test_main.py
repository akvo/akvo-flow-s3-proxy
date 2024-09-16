import io
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from app.dependencies import bucket_factory
from app.main import app

client = TestClient(app)


@pytest.fixture
def fake_bucket():
    fake_bucket = Mock(name="fake_bucket")
    app.dependency_overrides[bucket_factory] = lambda: lambda *_: fake_bucket
    yield fake_bucket
    app.dependency_overrides = {}


def test_healtz():
    response = client.get("/healtz")
    assert 200 == response.status_code
    assert {"status": "success", "message": "OK!"} == response.json()


def test_put_devicezip_should_call_bucket_upload(fake_bucket):
    fake_config = {"content": "not important"}
    file_name = "test.txt"
    file_content = io.BytesIO(b"<file content>")
    file_content_type = "text/plain"
    with patch("app.main.get_config", return_value=fake_config):
        client.put(
            "/instance1/devicezip/123/",
            files={"file": (file_name, file_content, file_content_type)},
        )
        fake_bucket.upload.assert_called()
        (_first_arg, second_arg, third_arg), _kwargs = fake_bucket.upload.call_args
        assert second_arg == f"devicezip/{file_name}"
        assert third_arg == {"ContentType": file_content_type}


def test_put_devicezip_with_invalid_instance_returns_404(fake_bucket):
    fake_config = {}
    with patch("app.main.get_config", return_value=fake_config):
        response = client.put(
            "/instance1/devicezip/123/",
            files={"file": io.BytesIO(b"<file content>")},
        )
        assert response.status_code == 404
        fake_bucket.upload.assert_not_called()


def test_put_images_should_call_bucket_upload(fake_bucket):
    fake_config = {"content": "not important"}
    file_name = "test.jpg"
    file_content = io.BytesIO(b"<file content>")
    file_content_type = "image/jpg"
    with patch("app.main.get_config", return_value=fake_config):
        client.put(
            "/instance1/images/123/",
            files={"file": (file_name, file_content, file_content_type)},
        )
        fake_bucket.upload.assert_called()
        (_first_arg, second_arg, third_arg), _kwargs = fake_bucket.upload.call_args
        assert second_arg == f"images/{file_name}"
        assert third_arg == {"ContentType": file_content_type, "ACL": "public-read"}


def test_put_images_with_invalid_instance_returns_404(fake_bucket):
    fake_config = {}
    with patch("app.main.get_config", return_value=fake_config):
        response = client.put(
            "/instance1/images/123/",
            files={"file": io.BytesIO(b"<file content>")},
        )
        assert response.status_code == 404
        fake_bucket.upload.assert_not_called()


def test_get_survey_form_should_call_bucket_download(fake_bucket):
    fake_config = {"content": "not important"}
    with patch("app.main.get_config", return_value=fake_config):
        client.get("/instance1/surveys/123.zip")
        fake_bucket.download.assert_called_with("surveys/123.zip")


def test_get_survey_form_with_invalid_instance_returns_404(fake_bucket):
    fake_config = {}
    with patch("app.main.get_config", return_value=fake_config):
        response = client.get("/instance1/images/file.txt")
        assert response.status_code == 404
        fake_bucket.download.assert_not_called()


def test_get_image_should_call_bucket_download(fake_bucket):
    fake_config = {"content": "not important"}
    with patch("app.main.get_config", return_value=fake_config):
        client.get("/instance1/images/file.txt")
        fake_bucket.download.assert_called_with("images/file.txt")


def test_get_image_with_invalid_instance_returns_404(fake_bucket):
    fake_config = {}
    with patch("app.main.get_config", return_value=fake_config):
        response = client.get("/instance1/images/file.txt")
        assert response.status_code == 404
        fake_bucket.download.assert_not_called()
