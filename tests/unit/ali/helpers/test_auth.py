import json

import pytest

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


def test_get_client_for_profile():
    with pytest.raises(Exception) as e:
        auth.extract_credentials_for_profile({})
        assert "invalid profile" in str(e)

    result = auth.extract_credentials_for_profile(
        {"mode": "AK", "access_key_id": "test-1", "access_key_secret": "test-2"}
    )

    assert result.access_key_id == "test-1"
    assert result.access_key_secret == "test-2"


def test_get_region_id_for_profile():
    with pytest.raises(Exception) as e:
        auth.extract_region_id_from_profile({})
        assert "invalid profile" in str(e)

    result = auth.extract_region_id_from_profile({"region_id": "cn-shanghai"})

    assert result == "cn-shanghai"


def test_get_config_file_contents(tmpdir, mocker):
    config_file = tmpdir.mkdir(".aliyun").join("config.json")
    config_file.write("Stuff that works!")

    mocked_home = mocker.patch("pathlib.Path.home")
    mocked_home.return_value = tmpdir

    result = auth._get_config_file_contents()

    assert result == "Stuff that works!"
