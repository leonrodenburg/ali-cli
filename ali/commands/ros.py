import click
import json

from aliyunsdkros.request.v20150901 import CreateStacksRequest


@click.group()
def ros():
    pass


@ros.command()
@click.option("--name", help="Stack name")
@click.option("--template-path", help="Path to JSON template")
@click.option(
    "--parameters",
    default="",
    help="Comma-separated list of key=val parameters to set in the template",
)
@click.option(
    "--timeout-mins",
    default=10,
    help="Timeout if stack was not created within specified minutes",
)
@click.pass_obj
def create_stack(obj, name, template_path, parameters, timeout_mins):
    """Creates an ROS stack"""
    with open(template_path, "r") as f:
        template = f.read()

    template_params = {}
    raw_params = parameters.split(",")
    for raw_param in raw_params:
        if len(raw_param) > 0 and "=" in raw_param:
            key, val = raw_param.split("=")
            template_params[key] = val

    request = CreateStacksRequest.CreateStacksRequest()
    request_body = {
        "Name": name,
        "TimeoutMins": timeout_mins,
        "Template": json.loads(template),
        "Parameters": template_params,
    }
    request.set_content_type("application/json")
    request.set_content(json.dumps(request_body).encode())

    client = obj["client"]
    client.do_action_with_exception(request)

    click.echo("Stack %s successfully deployed" % name)
