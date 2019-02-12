import click

from aliyunsdkcore.client import AcsClient

from ali.commands.configure import configure
from ali.commands.ros import ros

from ali.helpers import auth


@click.group()
@click.option("-p", "--profile", default="", help="CLI profile to load config for")
@click.pass_context
def cli(ctx, profile):
    """Ali CLI"""
    profile_obj = auth.extract_profile(profile)
    if not profile_obj:
        click.echo(
            "Could not locate credentials for Alibaba Cloud. Please run 'aliyun configure --profile <profile>' to set these up for a given profile."
        )

    access_key_id, access_key_secret, region_id = auth.extract_credentials(profile_obj)
    client = AcsClient(access_key_id, access_key_secret, region_id)
    ctx.obj = {"client": client}


cli.add_command(configure)
cli.add_command(ros)


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter,unexpected-keyword-arg
    cli(auto_envvar_prefix="ALI")
