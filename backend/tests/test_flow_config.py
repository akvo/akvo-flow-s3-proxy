import json
from pathlib import PosixPath
from typing import cast
from unittest.mock import patch

import pytest

from app.flow_config import get_config, populate, refresh


@pytest.fixture
def config_source(datadir: PosixPath) -> str:
    return str(datadir / "fake-flow-config")


@pytest.fixture
def config_file(tmp_path: PosixPath) -> str:
    return str(tmp_path / "config.json")


@pytest.fixture
def config(config_source: str, config_file: str) -> dict[str, dict[str, str]] | None:
    populate(source=config_source, destination=config_file)
    with open(config_file) as f:
        return json.load(f)


def test_happy_path(config: dict[str, dict[str, str]]):
    assert "one" in config
    assert "two" in config
    assert 2 == len(config)


def test_populate_ignore_no_survey_props(config: dict[str, dict[str, str]]):
    assert "no_survey_props" not in config


def test_populate_ignore_without_credential_file(config: dict[str, dict[str, str]]):
    assert "no_credential" not in config


def test_populate_ignore_without_app_id(config: dict[str, dict[str, str]]):
    assert "no_app_id" not in config
    assert "" not in config


def test_get_config(config_file: str, config):
    example: dict[str, str] = cast(
        dict[str, str], get_config("one", config_file=config_file)
    )
    assert example == config["one"]


@pytest.mark.internal
def test_get_config_call_populate_on_no_config_file(
    config_source: str, config_file: str
):
    def fake_populate(*_, **__):
        with open(config_file, "w") as f:
            json.dump([], f)

    with patch(
        "app.flow_config.populate", side_effect=fake_populate
    ) as mocked_populate:
        get_config("app_id", config_file=config_file, source=config_source)
        mocked_populate.assert_called_with(
            source=config_source, destination=config_file
        )


@pytest.mark.internal
def test_refresh_pull_git_repo_and_repopulate(config_source: str, config_file: str):
    with patch("app.flow_config.Git") as mocked_git:
        with patch("app.flow_config.populate") as mocked_populate:
            refresh(source=config_source, destination=config_file)
            mocked_git.assert_called_with(config_source)
            mocked_git_instance = mocked_git.return_value
            mocked_git_instance.pull.assert_called()
            mocked_populate.assert_called_with(
                source=config_source, destination=config_file
            )
