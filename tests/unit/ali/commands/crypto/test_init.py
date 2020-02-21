import os
from unittest import mock

from click.testing import CliRunner

from ali.commands.crypto import crypto

mock_obj = {"client": {}}


@mock.patch("ali.commands.crypto.Fernet")
def test_generate_key(mock_fernet):
    mock_fernet.generate_key.return_value = b"my-fancy-key"
    keyfile_path = os.path.join(os.getcwd(), ".test.key")

    runner = CliRunner()
    result = runner.invoke(crypto, ["generate-key", "-k", keyfile_path], obj=mock_obj)

    assert result.exception is None
    mock_fernet.generate_key.assert_called_once()

    with open(keyfile_path, "rb") as key:
        try:
            assert key.read() == b"my-fancy-key"
        finally:
            os.remove(keyfile_path)
