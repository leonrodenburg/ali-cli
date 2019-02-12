import click
import json
from pathlib import Path


@click.command()
@click.pass_obj
def configure(obj):
    click.echo(
        "Configuration through the `ali` command is currently unsupported. Please run `aliyun configure` instead."
    )
