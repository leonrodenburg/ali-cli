import json

import click
from aliyunsdkcr.request.v20160607 import GetAuthorizationTokenRequest

from ali.helpers.output import output_text


@click.group()
def cr():
    """Container Registry (CR)"""
    pass


@cr.command()
@click.pass_obj
def get_login(obj):
    """Output Docker login command for Container Registry"""
    request = GetAuthorizationTokenRequest.GetAuthorizationTokenRequest()
    client = obj["client"]
    response = json.loads(client.do_action_with_exception(request))

    username = response["data"]["tempUserName"]
    token = response["data"]["authorizationToken"]

    region = obj["region_id"]
    repository = f"registry-intl.{region}.aliyuncs.com"

    output = f"docker login -u {username} -p {token} {repository}"

    output_text(output)
