import os
import click
import oss2
import humanize
from cryptography.fernet import Fernet


@click.group()
def oss():
    """Commands for working with OSS with client-side encryption enabled"""
    pass


@oss.command()
@click.argument("local", type=click.Path(exists=True))
@click.argument("remote")
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
def upload(obj, local, remote, keyfile, recursive):
    """Encrypt and upload a local file or directory to an OSS bucket"""
    if not remote.startswith("oss://"):
        raise Exception(
            "Please specify an OSS URL (format: oss://<bucket>/<path>) for the remote URL"
        )

    local_files = []
    if os.path.isdir(local) and recursive:
        for dirname, _, files in os.walk(local):
            print(dirname)
            for file in files:
                if dirname.startswith("."):
                    dirname = dirname[1:]

                local_files.append(os.path.join(dirname, file).lstrip("/"))
    elif os.path.isdir(local) and not recursive:
        for entry in os.scandir(local):
            if entry.is_file():
                local_files.append(
                    os.path.join(local.lstrip("."), entry.name).lstrip("/")
                )
    else:
        local_files = [local]

    if len(local_files) > 1 and not remote.endswith("/"):
        raise Exception(
            "Can not upload multiple files to a file target, please specify a remote directory with /"
        )

    with open(keyfile, "rb") as f:
        key = f.read()

    bucket_name = remote.replace("oss://", "").split("/")[0]
    bucket_path = "/".join(remote.replace("oss://", "").split("/")[1:])
    if len(bucket_path) < 1:
        bucket_path = "/"

    for file in local_files:
        remote_path = (
            "%s%s" % (bucket_path, file) if bucket_path.endswith("/") else bucket_path
        ).lstrip("/")

        bucket = _get_oss_bucket(bucket_name, obj["client"])
        encrypted = _encrypt_file(file, key)

        bucket.put_object(remote_path, encrypted)

        click.secho(
            "Upload: %s -> %s (%s)"
            % (
                file,
                "oss//" + bucket_name + "/" + remote_path,
                humanize.naturalsize(len(encrypted), binary=True),
            )
        )


@oss.command()
@click.argument("remote")
@click.argument("local", type=click.Path())
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
def download(obj, remote, local, keyfile, recursive):
    """Download and decrypt OSS bucket contents to a local file or directory"""
    if not remote.startswith("oss://"):
        raise Exception(
            "Please specify an OSS URL (format: oss://<bucket>/<path>) for the remote URL"
        )

    bucket_name = remote.replace("oss://", "").split("/")[0]
    bucket_path = "/".join(remote.replace("oss://", "").split("/")[1:])
    bucket = _get_oss_bucket(bucket_name, obj["client"])

    remote_files = []
    if bucket_path == "" or bucket_path.endswith("/"):
        for obj in oss2.ObjectIterator(bucket, bucket_path):
            if recursive or "/" not in obj.key.replace(bucket_path, ""):
                remote_files.append(obj.key)
    else:
        remote_files = [bucket_path]

    if (bucket_path == "" or bucket_path.endswith("/")) and (
        (os.path.exists(local) and not os.path.isdir(local))
        or (not os.path.exists and local.endswith("/"))
    ):
        raise Exception(
            "Can not download multiple files to a local file, please specify a local directory"
        )

    with open(keyfile, "rb") as f:
        key = f.read()

    f = Fernet(key)

    for file in remote_files:
        remote_file = file

        if bucket_path == "" or bucket_path.endswith("/"):
            remote_file = remote_file.replace(bucket_path, "")
        else:
            remote_file = os.path.basename(remote_file)

        local_path = local
        if local.endswith("/") or os.path.isdir(local):
            local_path = os.path.join(local, remote_file)

        os.makedirs(os.path.dirname(local_path), 0o777, True)

        encrypted = bucket.get_object(file).read()
        decrypted = f.decrypt(encrypted)
        with open(local_path, "wb+") as local_file:
            local_file.write(decrypted)

        click.secho(
            "Download: %s -> %s (%s)"
            % (
                "oss//" + bucket_name + "/" + file,
                local_path,
                humanize.naturalsize(len(decrypted), binary=True),
            )
        )


def _get_oss_bucket(bucket_name, client):
    auth = oss2.Auth(client.get_access_key(), client.get_access_secret())
    return oss2.Bucket(
        auth, "http://oss-%s.aliyuncs.com" % (client.get_region_id()), bucket_name
    )


def _encrypt_file(path, key):
    with open(path, "rb") as f:
        unencrypted = f.read()
        f = Fernet(key)
        return f.encrypt(unencrypted)
