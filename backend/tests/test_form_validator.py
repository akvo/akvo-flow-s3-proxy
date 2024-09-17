from unittest.mock import patch

from app.form_validator import FormValidator


def test_validate_with_entity_exists():
    with patch("app.form_validator.Credentials.from_service_account_file"):
        with patch("app.form_validator.Client") as mocked_client:
            validator = FormValidator("fake-file.json")
            mocked_client_instance = mocked_client.return_value
            mocked_client_instance.get.return_value = {"value": "fake entity"}

            result = validator.validate(123)

            mocked_client_instance.key.asssert_called()
            mocked_client_instance.get.asssert_called()
            assert result


def test_validate_with_entity_not_exists():
    with patch("app.form_validator.Credentials.from_service_account_file"):
        with patch("app.form_validator.Client") as mocked_client:
            validator = FormValidator("fake-file.json")
            mocked_client_instance = mocked_client.return_value
            mocked_client_instance.get.return_value = None

            result = validator.validate(123)

            mocked_client_instance.key.asssert_called()
            mocked_client_instance.get.asssert_called()
            assert not result
