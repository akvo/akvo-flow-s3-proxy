# pyright: strict, reportCallIssue=false, reportArgumentType=false, reportReturnType=false

import json
import os
import re
import tempfile
from glob import glob

from git.cmd import Git

SOURCE_PATH = "/akvo-flow-server-config"
CONFIG_FILE = f"{tempfile.gettempdir()}/flow-config.json"
AWS_BUCKET = "awsBucket"
AWS_ACCESS_ID = "awsAccessKeyId"
AWS_SECRET = "awsSecretKey"
GCP_CREDENTIAL = "gcpCredentialFile"

instanceUrlPattern = re.compile(
    r"^(https?://)?(?P<alias>.+)+\.(akvoflow\.org|appspot\.com)$"
)


def populate(*, source: str = SOURCE_PATH, destination: str = CONFIG_FILE) -> None:
    files = glob(f"{source}/*/survey.properties")
    configs: dict[str, dict[str, str]] = {}
    for f in files:
        props = _parse_survey_props(f)
        path = os.path.dirname(f)
        app_id = _get_app_id(path)
        matches = instanceUrlPattern.match(props.get("instanceUrl", ""))
        if not matches:
            continue
        alias = matches.group("alias").strip()
        if not alias:
            continue
        gcp_credential_file = glob(f"{path}/{app_id}*.json")
        if not gcp_credential_file:
            continue
        props[GCP_CREDENTIAL] = gcp_credential_file[0]
        configs[alias] = props
    with open(destination, "w") as out:
        json.dump(configs, out)


def get_config(
    app_id: str, *, config_file: str = CONFIG_FILE, source: str = SOURCE_PATH
) -> dict[str, str] | None:
    if not os.path.isfile(config_file):
        populate(source=source, destination=config_file)
    with open(config_file) as f:
        config = json.load(f)
        return config[app_id] if app_id in config else None


def refresh(*, source: str = SOURCE_PATH, destination: str = CONFIG_FILE) -> None:
    repo = Git(source)
    repo.pull(rebase=True)
    populate(source=source, destination=destination)


def _parse_survey_props(filename: str) -> dict[str, str]:
    with open(filename) as f:
        content = f.read().split("\n")
        return dict(
            [tuple(t.strip() for t in line.split("=")) for line in content if line]  # type: ignore[misc]
        )


def _get_app_id(source_path: str) -> str:
    # The instance id used to come from <application> in appengine-web.xml.
    # Second-generation App Engine forbids that element -- the id comes from the
    # deploy command instead -- so every descriptor in akvo-flow-server-config had
    # it stripped, and reading it here returned nothing for all 110 instances: each
    # one was skipped, and every mobile app got a 404 for form downloads and data
    # uploads. The directory holding the descriptor is the id, which is what
    # akvo.commons falls back to as well, and a directory cannot go missing or
    # drift from itself the way an element can.
    return os.path.basename(source_path)
