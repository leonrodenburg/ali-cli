import json

import click
from aliyunsdkros.request.v20150901 import (
    CreateStacksRequest,
    DeleteStackRequest,
    DescribeStackDetailRequest,
    DescribeStacksRequest,
)

from ali.helpers.template import template_to_string, load_template
from ali.helpers.output import output_json, output_success


@click.group()
def ros():
    pass


@ros.command()
@click.option("--name", help="Stack name", required=True)
@click.option(
    "--template",
    help="JSON template (path or - to supply through stdin)",
    required=True,
    type=click.File("r"),
)
@click.option(
    "--parameters",
    default=[],
    multiple=True,
    help="Comma-separated list of key=val parameters to set in the template",
)
@click.option(
    "--timeout-mins",
    default=10,
    help="Timeout if stack was not created within specified minutes",
)
@click.pass_obj
def create_stack(obj, name, template, parameters, timeout_mins):
    """Creates an ROS stack"""
    body = load_template(template)

    template_params = {}
    for raw_param in parameters:
        if len(raw_param) > 0 and "=" in raw_param:
            key, val = raw_param.split("=")
            template_params[key] = val

    request = CreateStacksRequest.CreateStacksRequest()
    request_body = {
        "Name": name,
        "TimeoutMins": timeout_mins,
        "Template": body,
        "Parameters": template_params,
    }
    request.set_content_type("application/json; encoding=utf-8")
    request.set_content(template_to_string(request_body).encode("utf-8"))

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
    """Get all details of a single stack, including parameters"""
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
