"""A small hack to write boto files with required information for gsutil.

I should probably just work without gsutil soon...
"""
from __future__ import annotations

import os
import json
import subprocess
from textwrap import dedent
from collections import namedtuple


AWSKeys = namedtuple("AWSKeys", ["access_key_id", "secret_access_key"])
TDKeys = namedtuple("TDKeys", ["access_key_id", "secret_access_key"])
HOME = os.path.expanduser("~")
AWSPATH = os.path.join(HOME, ".cloudvolume/secrets", "aws-secret.json")
GCPPATH = os.path.join(HOME, ".cloudvolume/secrets", "google-secret.json")
TDPATH = os.path.join(HOME, ".cloudvolume/secrets", "tigerdata-secret.json")
BOTOPATH = os.path.join(HOME, ".boto")


def gcloud_configured():
    """Tests whether gcloud permissions are set by trying gsutil."""
    if not os.path.isfile(GCPPATH):
        return False

    projectid = read_gcp_project()

    cmd = "gsutil ls"
    if projectid is not None:
        cmd += f" -p {projectid}"

    status, _ = subprocess.getstatusoutput(cmd)

    return status == 0


def writeboto() -> None:
    """Writes a boto file for gsutil using the CloudVolume secret files."""
    awskeys = read_aws_keys() if os.path.isfile(AWSPATH) else None
    projectid = read_gcp_project() if os.path.isfile(GCPPATH) else None
    tdkeys = read_td_keys() if os.path.isfile(TDPATH) else None

    if awskeys or projectid or tdkeys:
        if not os.path.isfile(BOTOPATH):
            _writeboto(BOTOPATH, awskeys, projectid, tdkeys)


def read_aws_keys(path: str = AWSPATH):
    """Reads the AWS credential keys from the secret json file."""
    with open(path) as f:
        content = json.load(f)

    return AWSKeys(content["AWS_ACCESS_KEY_ID"], content["AWS_SECRET_ACCESS_KEY"])


def read_td_keys(path: str = TDPATH):
    """Reads the Tigerdata credential keys from the secret json file."""
    with open(path) as f:
        content = json.load(f)

    return TDKeys(content["ACCESS_KEY_ID"], content["SECRET_ACCESS_KEY"])


def read_gcp_project(path: str = GCPPATH):
    """Reads the google cloud project name from the secret json file."""
    with open(path) as f:
        content = json.load(f)

    return content["project_id"]


def _writeboto(path: str, awskeys: AWSKeys, projectid: str, tdkeys: TDKeys) -> None:
    with open(path, "w+") as f:
        f.write(dedent("[Credentials]\n\n"))

        if awskeys is not None:
            f.write(f"aws_access_key_id = {awskeys.access_key_id}\n\n")
            f.write(f"aws_secret_acces_key = {awskeys.secret_access_key}\n\n")

        if tdkeys is not None:
            f.write(f"access_key_id = {tdkeys.access_key_id}\n\n")
            f.write(f"secret_acces_key = {tdkeys.secret_access_key}\n\n")

        f.write(f"gs_service_key_file = {GCPPATH}\n\n")

        f.write(
            dedent(
                """
                [Boto]

                https_validate_certificates = True


                [GoogleCompute]

                [GSUtil]

                content_language = en

                default_api_version = 2

                """
            )
        )

        if projectid is not None:
            f.write(f"default_project_id = {projectid}\n\n")

        f.write("[OAuth2]\n")
