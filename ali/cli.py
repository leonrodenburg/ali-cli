import click
import sys
from aliyunsdkcore.client import AcsClient

from ali.commands.configure import configure
from ali.commands.cr import cr
from ali.commands.crypto import crypto
from ali.commands.kms import kms
from ali.commands.mns import mns
from ali.commands.params import params
from ali.commands.ros import ros
from ali.helpers import auth
from ali.helpers.output import output_error


@click.group(context_settings=dict(max_content_width=160), invoke_without_command=True)
@click.option("-p", "--profile", default="", help="CLI profile to load config for")
@click.option("--version", is_flag=True, help="Output CLI version and exit")
@click.pass_context
def cli(ctx, profile, version):
    """Ali CLI (v0.7.3)"""
    if version:
        click.echo("Ali CLI (v0.7.3)")
        exit(0)
    elif ctx.invoked_subcommand is None:
        click.echo(ctx.command.get_help(ctx))
        exit(0)

    profile_obj = auth.extract_profile(profile)
    if not profile_obj:
        raise Exception(
            "Could not locate credentials for Alibaba Cloud. Please run 'aliyun configure --profile <profile>' to set these up for a given profile."
        )

    credentials = auth.extract_credentials_for_profile(profile_obj)
    region_id = auth.extract_region_id_from_profile(profile_obj)
    ctx.obj = {
        "client": AcsClient(region_id=region_id, credential=credentials),
        "region_id": region_id,
        "credentials": credentials,
    }


cli.add_command(configure)
cli.add_command(cr)
cli.add_command(crypto)
cli.add_command(kms)
cli.add_command(mns)
cli.add_command(ros)
cli.add_command(params)


def _handle_exception(e):
    output_error(e)


def safe_cli():
    # pylint: disable=no-value-for-parameter,unexpected-keyword-arg
    try:
        cli(auto_envvar_prefix="ALI")
    except Exception as e:
        _handle_exception(e)
        sys.exit(1)


if __name__ == "__main__":
    safe_cli()
