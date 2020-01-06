import json
from unittest import mock

import aliyunsdkcore
import pytest
from aliyunsdkcore.auth.credentials import AccessKeyCredential
from aliyunsdkcore.client import AcsClient

from ali.helpers import auth


def test_extract_profile(mocker):
    valid_config = {
        "current": "test",
        "profiles": [
            {"name": "test", "dinner": "pancakes"},
            {"name": "test2", "dinner": "pizza"},
        ],
    }

    mocked_get_config_file = mocker.patch("ali.helpers.auth._get_config_file_contents")
    mocked_get_config_file.return_value = json.dumps(valid_config)

    found = auth.extract_profile()

    assert found["dinner"] == "pancakes"

    found = auth.extract_profile("test2")
    assert found["dinner"] == "pizza"

    with pytest.raises(Exception):
        invalid_config = {}
        mocked_get_config_file.return_value = json.dumps(invalid_config)
        auth.extract_profile()


def test_get_client_for_profile(mocker):
    client_spy = mocker.spy(AcsClient, "__init__")

    with pytest.raises(Exception) as e:
        auth.get_client_for_profile({})
        assert "invalid profile" in str(e)

    auth.get_client_for_profile({
        "mode": "AK",
        "access_key_id": "test-1",
        "access_key_secret": "test-2",
        "region_id": "cn-shanghai"
    })
    client_spy.assert_called_once()
    args = client_spy.call_args[1]
    
    assert args["region_id"] == "cn-shanghai"
    assert args["credential"].access_key_id == "test-1"
    assert args["credential"].access_key_secret == "test-2"


def test_get_config_file_contents(tmpdir, mocker):
    config_file = tmpdir.mkdir(".aliyun").join("config.json")
    config_file.write("Stuff that works!")

    mocked_home = mocker.patch("pathlib.Path.home")
    mocked_home.return_value = tmpdir

    result = auth._get_config_file_contents()

    assert result == "Stuff that works!"
