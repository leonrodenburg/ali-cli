import sys

import click
from aliyunsdkcore.client import AcsClient

from ali.commands.configure import configure
from ali.commands.crypto import crypto
from ali.commands.kms import kms
from ali.commands.mns import mns
from ali.commands.ros import ros
from ali.helpers import auth
from ali.helpers.output import output_error


@click.group(context_settings=dict(max_content_width=160))
@click.option("-p", "--profile", default="", help="CLI profile to load config for")
@click.pass_context
def cli(ctx, profile):
    """Ali CLI"""
    profile_obj = auth.extract_profile(profile)
    if not profile_obj:
        raise Exception(
            "Could not locate credentials for Alibaba Cloud. Please run 'aliyun configure --profile <profile>' to set these up for a given profile."
        )

    access_key_id, access_key_secret, region_id = auth.extract_credentials(profile_obj)
    client = AcsClient(access_key_id, access_key_secret, region_id)
    ctx.obj = {"client": client}


cli.add_command(configure)
cli.add_command(crypto)
cli.add_command(kms)
cli.add_command(mns)
cli.add_command(ros)


def _handle_exception(e):
    output_error(e)


def safe_cli():
    # pylint: disable=no-value-for-parameter,unexpected-keyword-arg
    try:
        cli(auto_envvar_prefix="ALI")
    except Exception as e:
        _handle_exception(e)
        sys.exit()


if __name__ == "__main__":
    safe_cli()
