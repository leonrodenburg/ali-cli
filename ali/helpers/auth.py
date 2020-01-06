import json
from pathlib import Path

from aliyunsdkcore.auth.credentials import (
    StsTokenCredential,
    EcsRamRoleCredential,
    RamRoleArnCredential,
    AccessKeyCredential,
)


def extract_profile(profile=""):
    config = _get_config_file_contents()
    config = json.loads(config)

    current = profile
    if len(current) < 1 and "current" in config:
        current = config["current"]

    found = list(filter(lambda p: p["name"] == current, config["profiles"]))
    if len(found) > 0:
        return found[0]
    else:
        raise Exception(
            "Invalid profile specified or no profiles configured at all (run 'aliyun configure')"
        )


def extract_credentials_for_profile(profile):
    if profile["mode"] == "AK":
        return AccessKeyCredential(
            profile["access_key_id"], profile["access_key_secret"]
        )
    elif profile["mode"] == "StsToken":
        return StsTokenCredential(
            profile["access_key_id"], profile["access_key_secret"], profile["sts_token"]
        )
    elif profile["mode"] == "RamRoleArn":
        return RamRoleArnCredential(
            profile["access_key_id"],
            profile["access_key_secret"],
            profile["ram_role_arn"],
            profile["ram_role_name"],
        )
    elif profile["mode"] == "EcsRamRole":
        return EcsRamRoleCredential(profile["ram_role_name"])
    else:
        raise Exception(
            "Tried to extract credentials from invalid profile: '%s'"
            % (profile["name"])
        )


def extract_region_id_from_profile(profile):
    if "region_id" in profile:
        return profile["region_id"]

    raise Exception(
        "Tried to extract region from invalid profile: '%s'" % profile["name"]
    )


def _get_config_file_contents():
    home = Path.home()
    config_dir = home / ".aliyun"
    config_file = config_dir / "config.json"
    with config_file.open() as f:
        config = f.read()
    return config
