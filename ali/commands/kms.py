import click
from aliyunsdkkms.request.v20160120 import (
    EncryptRequest,
    DecryptRequest,
    GenerateDataKeyRequest,
    ListKeysRequest,
)

from ali.helpers.output import output_json


@click.group()
def kms():
    """Key Management Service (KMS)"""
    pass


@kms.command()
@click.option("--page-number", help="Page number to fetch", default=1)
@click.option("--page-size", help="Page size", default=10)
@click.pass_obj
def list_keys(obj, page_number, page_size):
    """Fetch a list of Customer Master Keys (CMK)"""
    request = ListKeysRequest.ListKeysRequest()
    request.set_PageNumber(page_number)
    request.set_PageSize(page_size)

    client = obj["client"]
    response = client.do_action_with_exception(request)
    output_json(response)


@kms.command()
@click.option("--key-id", help="Customer Master Key (CMK) ID to use", required=True)
@click.option("--value", help="Plaintext string to encrypt", required=True)
@click.pass_obj
def encrypt(obj, key_id, value):
    """Encrypt a plaintext value using a Customer Master Key (CMK) (not recommended)"""
    request = EncryptRequest.EncryptRequest()
    request.set_KeyId(key_id)
    request.set_Plaintext(value)

    client = obj["client"]
    response = client.do_action_with_exception(request)
    output_json(response)


@kms.command()
@click.option("--blob", help="Ciphertext blob to decrypt", required=True)
@click.pass_obj
def decrypt(obj, blob):
    """Decrypt a ciphtertext blob using a Customer Master Key (CMK)"""
    request = DecryptRequest.DecryptRequest()
    request.set_CiphertextBlob(blob)

    client = obj["client"]
    response = client.do_action_with_exception(request)
    output_json(response)


@kms.command()
@click.option("--key-id", help="Customer Master Key (CMK) ID to use", required=True)
@click.option(
    "--key-spec",
    type=click.Choice(["AES_256", "AES_128"]),
    help="Cipher to use for data key (AES_256 = default or AES_128)",
    default="AES_256",
)
@click.pass_obj
def generate_data_key(obj, key_id, key_spec):
    """Generate a data key that can be used to encrypt a piece of data (recommended)"""
    request = GenerateDataKeyRequest.GenerateDataKeyRequest()
    request.set_KeyId(key_id)
    request.set_KeySpec(key_spec)

    client = obj["client"]
    response = client.do_action_with_exception(request)
    output_json(response)
