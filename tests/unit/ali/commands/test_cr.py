import json
from unittest import mock

from click.testing import CliRunner

from ali.commands.cr import cr


def test_get_login():
    mock_client = mock.MagicMock()
    mock_obj = {"client": mock_client, "region_id": "cn-shanghai"}

    mock_client.do_action_with_exception.return_value = json.dumps(
        {"data": {"tempUserName": "test", "authorizationToken": "123456abcdef"}}
    )

    runner = CliRunner()
    result = runner.invoke(cr, ["get-login"], obj=mock_obj)

    assert (
        result.output.rstrip()
        == "docker login -u test -p 123456abcdef registry-intl.cn-shanghai.aliyuncs.com"
    )
