import json

import click
from oss2.exceptions import NoSuchKey, NoSuchBucket, NotFound, AccessDenied
from oss2.headers import RequestHeader
from oss2.models import ServerSideEncryptionRule, SERVER_SIDE_ENCRYPTION_KMS

from ali.helpers.oss import get_bucket
from ali.helpers.output import output_json


@click.group()
def params():
    """Store parameters in a user-defined namespace (uses OSS bucket for storage)"""
    pass


@params.command()
@click.option("-n", "--namespace", help="Namespace of the parameter", required=True)
@click.option(
    "-p",
    "--path",
    help="Path of the parameter (can be any directory path)",
    required=True,
)
@click.option("-d", "--data", help="Data to put", required=True)
@click.option(
    "-f",
    "--force",
    help="Force override existing parameter",
    required=False,
    default=False,
    is_flag=True,
)
@click.pass_obj
def put(obj, namespace, path, data, force):
    """Write a custom parameter to a namespace"""
    bucket = get_bucket(namespace, obj)

    try:
        bucket.get_bucket_info()
    except NoSuchBucket:
        bucket.create_bucket()
        bucket.put_bucket_encryption(
            ServerSideEncryptionRule(SERVER_SIDE_ENCRYPTION_KMS)
        )
    except AccessDenied:
        raise Exception("Namespace does not belong to you (permission denied)")

    try:
        object_meta = bucket.get_object_meta(path)
        if not force and object_meta:
            raise Exception(
                "Parameter '%s' in namespace '%s' already exists (use --force to override)"
                % (path, bucket.bucket_name)
            )
    except NoSuchKey:
        pass

    headers = RequestHeader()
    headers.set_server_side_encryption(SERVER_SIDE_ENCRYPTION_KMS)
    headers["x-oss-meta-ali-param"] = "1"
    bucket.put_object(path, data, headers=headers)

    response = {"Namespace": namespace, "Path": path}
    output_json(json.dumps(response))


@params.command()
@click.option("-n", "--namespace", help="Namespace of the parameter", required=True)
@click.option("-p", "--path", help="Path of the parameter to get", required=True)
@click.option(
    "-f",
    "--format",
    help="Output format (json / text)",
    required=False,
    type=click.Choice(["json", "text"]),
    default="json",
)
@click.pass_obj
def get(obj, namespace, path, format):
    """Get the value of a parameter from a namespace"""
    bucket = get_bucket(namespace, obj)

    try:
        meta = bucket.head_object(path)
    except NotFound:
        raise Exception(
            "Parameter '%s' not found in namespace '%s'" % (path, namespace)
        )
    except AccessDenied:
        raise Exception(
            "Parameter '%s' in namespace '%s' does not belong to you (permission denied)"
            % (path, namespace)
        )

    if (
        "x-oss-meta-ali-param" not in meta.headers
        or meta.headers["x-oss-meta-ali-param"] != "1"
    ):
        raise Exception(
            "Parameter with path '%s' in namespace '%s' not created by Ali CLI"
            % (path, namespace)
        )

    content = bucket.get_object(path).read()
    if format == "json":
        response = {
            "Namespace": namespace,
            "Path": path,
            "Data": content.decode("utf-8"),
        }
        output_json(json.dumps(response))
    elif format == "text":
        click.secho(content.decode("utf-8"))
    else:
        raise Exception("Invalid output format selected")


@params.command()
@click.option("-n", "--namespace", help="Namespace of the parameter", required=True)
@click.option("-p", "--path", help="Path of the parameter to put", required=True)
@click.pass_obj
def delete(obj, namespace, path):
    """Delete a custom parameter from a namespace"""
    bucket = get_bucket(namespace, obj)

    try:
        meta = bucket.head_object(path)
    except NotFound:
        raise Exception(
            "Parameter '%s' not found in namespace '%s'" % (path, namespace)
        )
    except AccessDenied:
        raise Exception(
            "Parameter '%s' in namespace '%s' does not belong to you (permission denied)"
            % (path, namespace)
        )

    if meta.headers["x-oss-meta-ali-param"] != "1":
        raise Exception("Cannot delete parameter that was not created through Ali CLI")

    bucket.delete_object(path)
