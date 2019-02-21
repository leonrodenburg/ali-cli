import pytest
import io
import json
import tempfile

from ali.helpers import auth


def test_extract_profile(mocker):
    valid_config = {"profiles": [{"name": "test", "dinner": "pancakes"}]}

    mocked_get_config_file = mocker.patch("ali.helpers.auth._get_config_file_contents")
    mocked_get_config_file.return_value = json.dumps(valid_config)

    found = auth.extract_profile()

    assert found == None

    found = auth.extract_profile("test")
    assert found["dinner"] == "pancakes"

    with pytest.raises(Exception):
        invalid_config = {}
        mocked_get_config_file.return_value = json.dumps(invalid_config)
        auth.extract_profile()


def test_extract_credentials():
    valid_profile_obj = {
        "access_key_id": "1234567890",
        "access_key_secret": "abcdefgh",
        "region_id": "home-sweet-home",
    }

    access_key_id, access_key_secret, region_id = auth.extract_credentials(
        valid_profile_obj
    )

    assert access_key_id == "1234567890"
    assert access_key_secret == "abcdefgh"
    assert region_id == "home-sweet-home"

    with pytest.raises(Exception):
        invalid_profile_obj = {}
        auth.extract_credentials(invalid_profile_obj)


def test_get_config_file_contents(tmpdir, mocker):
    config_file = tmpdir.mkdir(".aliyun").join("config.json")
    config_file.write("Stuff that works!")

    mocked_home = mocker.patch("pathlib.Path.home")
    mocked_home.return_value = tmpdir

    result = auth._get_config_file_contents()

    assert result == "Stuff that works!"
