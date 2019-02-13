import click
import json

from aliyunsdkros.request.v20150901 import CreateStacksRequest
from aliyunsdkros.request.v20150901 import DeleteStackRequest
from aliyunsdkros.request.v20150901 import DescribeStacksRequest
from aliyunsdkros.request.v20150901 import DescribeStackDetailRequest

from ali.helpers.output import output_json, output_success


@click.group()
def ros():
    pass


@ros.command()
@click.option("--name", help="Stack name", required=True)
@click.option("--template-path", help="Path to JSON template", required=True)
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
    response = client.do_action_with_exception(request)

    output_success("Stack '%s' created successfully" % name)
    output_json(response)


@ros.command()
@click.option("--name", help="Stack name", required=True)
@click.pass_obj
def delete_stack(obj, name):
    """Delete an ROS stack and its resources"""
    stack = _find_stack_by_name(obj["client"], name)

    request = DeleteStackRequest.DeleteStackRequest()
    request.add_path_param("StackName", name)
    request.add_path_param("StackId", stack["Id"])

    client = obj["client"]
    client.do_action_with_exception(request)

    output_success("Stack '%s' successfully deleted" % name)


@ros.command()
@click.pass_obj
def describe_stacks(obj):
    """List stacks in the current region"""
    request = DescribeStacksRequest.DescribeStacksRequest()

    client = obj["client"]
    response = client.do_action_with_exception(request)

    output_json(response)


@ros.command()
@click.option("--name", help="Stack name", required=True)
@click.pass_obj
def describe_stack(obj, name):
    stack = _find_stack_by_name(obj["client"], name)

    request = DescribeStackDetailRequest.DescribeStackDetailRequest()
    request.add_path_param("StackName", name)
    request.add_path_param("StackId", stack["Id"])

    client = obj["client"]
    response = client.do_action_with_exception(request)

    output_json(response)


def _find_stack_by_name(client, name):
    stacks_request = DescribeStacksRequest.DescribeStacksRequest()

    stacks_response = json.loads(client.do_action_with_exception(stacks_request))
    stacks = list(filter(lambda s: s["Name"] == name, stacks_response["Stacks"]))
    if len(stacks) == 0:
        raise Exception("Could not find the specified stack")

    return stacks[0]
