import os
import tempfile
from unittest import mock

from click.testing import CliRunner
from cryptography.fernet import Fernet

from ali.commands.crypto.oss import group

mock_obj = {"client": {}, "region_id": "cn-shanghai", "credentials": {}}
mock_bucket = mock.MagicMock()


@mock.patch("ali.commands.crypto.oss.get_bucket", new=mock.MagicMock(return_value=mock_bucket))
@mock.patch("ali.commands.crypto.oss.Fernet")
def test_upload(mock_fernet):
    fernet = mock_fernet.return_value
    fernet.encrypt.return_value = "fancy_encrypted_value"

    value = b"Hello world!"
    temp_url = tempfile.NamedTemporaryFile(mode="wb+")
    os.chmod(temp_url.name, 0o777)
    temp_url.write(value)
    temp_url.seek(0)

    key = Fernet.generate_key()
    temp_key = tempfile.NamedTemporaryFile(mode="wb+")
    temp_key.write(key)
    temp_key.seek(0)

    runner = CliRunner()
    result = runner.invoke(
        group,
        ["upload", temp_url.name, "oss://test/file.txt", "-k", temp_key.name],
        obj=mock_obj,
    )

    assert result.exception is None
    assert result.exit_code == 0

    mock_fernet.assert_called_once_with(key)
    mock_bucket.put_object.assert_called_once_with("file.txt", "fancy_encrypted_value")
