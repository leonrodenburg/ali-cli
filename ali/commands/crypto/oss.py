import os

import click
import humanize
import oss2
from cryptography.fernet import Fernet

from ali.helpers.oss import get_bucket


@click.group()
def group():
    """Commands for working with OSS with client-side encryption enabled"""
    pass


@group.command()
@click.argument("url1")
@click.argument("url2")
@click.option(
    "-k",
    "--keyfile",
    required=True,
    help="Keyfile to use to encrypt files",
    type=click.Path(exists=True),
)
@click.option(
    "-r",
    "--recursive",
    is_flag=True,
    required=False,
    help="Recursively upload all files and folders in local path",
)
@click.pass_obj
@click.pass_context
def cp(ctx, obj, url1, url2, keyfile, recursive):
    """Encrypt and copy files from a local to a OSS file or directory, or vice versa"""
    if url1.startswith("oss://"):
        ctx.forward(download)
    else:
        ctx.forward(upload)


@group.command()
@click.argument("url1", type=click.Path(exists=True))
@click.argument("url2")
@click.option(
    "-k",
    "--keyfile",
    required=True,
    help="Keyfile to use to encrypt files",
    type=click.Path(exists=True),
)
@click.option(
    "-r",
    "--recursive",
    is_flag=True,
    required=False,
    help="Recursively upload all files and folders in local path",
)
@click.pass_obj
def upload(obj, url1, url2, keyfile, recursive):
    """Encrypt and upload a local file or directory to an OSS bucket"""
    if not url2.startswith("oss://"):
        raise Exception(
            "Please specify an OSS URL (format: oss://<bucket>/<path>) for the remote URL"
        )

    local_files = []
    if os.path.isdir(url1) and recursive:
        for dirname, _, files in os.walk(url1):
            for file in files:
                if dirname.startswith("."):
                    dirname = dirname[1:]

                local_files.append(os.path.join(dirname, file).lstrip("/"))
    elif os.path.isdir(url1) and not recursive:
        for entry in os.scandir(url1):
            if entry.is_file():
                local_files.append(
                    os.path.join(url1.lstrip("."), entry.name).lstrip("/")
                )
    else:
        local_files = [url1]

    bucket_name = url2.replace("oss://", "").split("/")[0]
    bucket_path = "/".join(url2.replace("oss://", "").split("/")[1:])
    if len(bucket_path) < 1:
        bucket_path = "/"

    if os.path.isdir(url1) and not bucket_path.endswith("/"):
        raise Exception(
            "Can not upload multiple local files to a single remote file, please specify a remote directory that ends with /"
        )

    key = _read_keyfile(keyfile)
    f = Fernet(key)

    for file in local_files:
        remote_path = (
            "%s%s" % (bucket_path, os.path.basename(file))
            if bucket_path.endswith("/")
            else bucket_path
        ).lstrip("/")

        bucket = get_bucket(bucket_name, obj)

        with open(file, "rb") as local_file:
            decrypted = local_file.read()
            encrypted = f.encrypt(decrypted)

            print(bucket)
            bucket.put_object(remote_path, encrypted)

        click.secho(
            "Upload: %s -> %s (%s)"
            % (
                file,
                "oss://" + bucket_name + "/" + remote_path,
                humanize.naturalsize(len(encrypted), binary=True),
            )
        )


@group.command()
@click.argument("url1")
@click.argument("url2", type=click.Path())
@click.option(
    "-k",
    "--keyfile",
    required=True,
    help="Keyfile to use to encrypt files",
    type=click.Path(exists=True),
)
@click.option(
    "-r",
    "--recursive",
    is_flag=True,
    required=False,
    help="Recursively download all files and folders in local path",
)
@click.pass_obj
def download(obj, url1, url2, keyfile, recursive):
    """Download and decrypt OSS bucket contents to a local file or directory"""
    if not url1.startswith("oss://"):
        raise Exception(
            "Please specify an OSS URL (format: oss://<bucket>/<path>) for the remote URL"
        )

    if url2 == "." or url2 == "..":
        url2 = url2 + "/"

    bucket_name = url1.replace("oss://", "").split("/")[0]
    bucket_path = "/".join(url1.replace("oss://", "").split("/")[1:])
    bucket = get_bucket(bucket_name, obj)

    remote_files = []
    if bucket_path == "" or bucket_path.endswith("/"):
        for obj in oss2.ObjectIterator(bucket, bucket_path):
            if recursive or "/" not in obj.key.replace(bucket_path, ""):
                remote_files.append(obj.key)
    else:
        remote_files = [bucket_path]

    if (bucket_path == "" or bucket_path.endswith("/")) and not url2.endswith("/"):
        raise Exception(
            "Can not download multiple remote files to a single local file, please specify a local directory that ends with /"
        )

    key = _read_keyfile(keyfile)
    f = Fernet(key)

    for file in remote_files:
        remote_file = file

        if bucket_path == "" or bucket_path.endswith("/"):
            remote_file = remote_file.replace(bucket_path, "")
        else:
            remote_file = os.path.basename(remote_file)

        local_path = url2
        if url2.endswith("/") or os.path.isdir(url2):
            local_path = os.path.join(url2, remote_file)

        os.makedirs(os.path.dirname(local_path), 0o777, True)

        encrypted = bucket.get_object(file).read()
        decrypted = f.decrypt(encrypted)
        with open(local_path, "wb+") as local_file:
            local_file.write(decrypted)

        click.secho(
            "Download: %s -> %s (%s)"
            % (
                "oss://" + bucket_name + "/" + file,
                local_path,
                humanize.naturalsize(len(decrypted), binary=True),
            )
        )


def _read_keyfile(keyfile):
    with open(keyfile, "rb") as f:
        return f.read()
