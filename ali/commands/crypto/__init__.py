import os

import click
from cryptography.fernet import Fernet

from ali.commands.crypto.oss import group
from ali.helpers.output import output_success


@click.group()
def crypto():
    """Cryptography functions"""
    pass


crypto.add_command(group, name="oss")


@crypto.command()
@click.option(
    "-k",
    "--keyfile",
    help="Filename to store secret key in",
    required=True,
    type=click.Path(),
)
def generate_key(keyfile):
    """Generate a secret key for symmetric cryptography"""
    if os.path.exists(keyfile):
        raise Exception("Unable to store secret key in %s: file exists" % keyfile)

    key = Fernet.generate_key()

    with open(keyfile, "wb") as f:
        f.write(key)

    output_success("Successfully created secret key in %s" % keyfile)


@crypto.command()
@click.option(
    "-k",
    "--keyfile",
    help="Filename of the secret key used to encrypt",
    required=True,
    type=click.Path(exists=True),
)
@click.option("-s", "--string", help="Plaintext string to encrypt", required=False)
@click.option(
    "-f",
    "--file",
    help="Plaintext file to encrypt",
    required=False,
    type=click.Path(exists=True),
)
@click.option(
    "-o",
    "--output",
    help="Output result to this file",
    required=False,
    type=click.Path(),
)
def encrypt(keyfile, string="", file=None, output=None):
    """Encrypt data using a secret key file"""
    if not string and not file:
        raise Exception("Please specify a string or a file to encrypt")

    with open(keyfile, "rb") as f:
        key = f.read()

    plaintext = string
    if not string:
        with open(file, "r") as f:
            plaintext = f.read()

    f = Fernet(key)
    encrypted = f.encrypt(bytes(plaintext, "utf-8"))

    if output:
        with open(output, "wb") as outputf:
            outputf.write(encrypted)
    else:
        click.secho(encrypted.decode("utf-8"))


@crypto.command()
@click.option(
    "-k",
    "--keyfile",
    help="Filename of the secret key used to encrypt",
    required=True,
    type=click.Path(exists=True),
)
@click.option("-s", "--string", help="Ciphertext string to decrypt", required=False)
@click.option(
    "-f",
    "--file",
    help="Ciphertext file to decrypt",
    required=False,
    type=click.Path(exists=True),
)
@click.option(
    "-o",
    "--output",
    help="Output result to this file",
    required=False,
    type=click.Path(),
)
def decrypt(keyfile, string="", file=None, output=None):
    """Decrypt data using a secret key file"""
    if not string and not file:
        raise Exception("Please specify a string or a file to decrypt")

    with open(keyfile, "rb") as keyf:
        key = keyf.read()

    f = Fernet(key)
    value = string
    if not string:
        with open(file, "r") as dataf:
            value = dataf.read()

    decrypted = f.decrypt(bytes(value, "utf-8"))

    if output:
        with open(output, "wb") as outputf:
            outputf.write(decrypted)
    else:
        click.secho(decrypted.decode("utf-8"))
