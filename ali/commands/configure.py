import click


@click.command()
@click.pass_obj
def configure(obj):
    """Initialize CLI with an access key """
    click.echo(
        "Configuration through the `ali` command is currently unsupported. Please run `aliyun configure` instead."
    )
