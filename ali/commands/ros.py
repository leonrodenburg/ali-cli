import json
import re
from typing import NamedTuple

import click
from aliyunsdkros.request.v20150901 import (
    CreateStacksRequest,
    DeleteStackRequest,
    DescribeResourcesRequest,
    DescribeStackDetailRequest,
    DescribeStacksRequest,
    UpdateStackRequest,
)

from ali.helpers.output import output_json, output_success
from ali.helpers.template import template_to_string, load_template


class RosParameter(NamedTuple):
    name: str
    value: object


class RosParameterType(click.ParamType):
    name = "parameter"

    def convert(self, value, param, ctx):
        found = re.match(r"(?P<name>[^=][^=]*)=(?P<value>.*)", value)

        if not found:
            self.fail(f"{value} should match <name>=<value>", param, ctx)

        return RosParameter(found.group("name"), found.group("value"))


@click.group()
def ros():
    """Resource Orchestration Service (ROS)"""
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
    "--parameter",
    default=[],
    type=RosParameterType(),
    multiple=True,
    help="Comma-separated list of key=val parameters to set in the template",
)
@click.option(
    "--timeout-mins",
    default=10,
    help="Timeout if stack was not created within specified minutes",
)
@click.pass_obj
def create_stack(obj, name, template, parameter, timeout_mins):
    """Creates a ROS stack"""
    body = load_template(template)
    request = CreateStacksRequest.CreateStacksRequest()
    request_body = {
        "Name": name,
        "TimeoutMins": timeout_mins,
        "Template": body,
        "Parameters": {p.name: p.value for p in parameter},
    }
    request.set_content_type("application/json; encoding=utf-8")
    request.set_content(template_to_string(request_body).encode("utf-8"))

    client = obj["client"]
    response = client.do_action_with_exception(request)

    output_success("Stack '%s' created successfully" % name)
    output_json(response)


@ros.command()
@click.option("--name", help="Stack name", required=True)
@click.option(
    "--template",
    help="JSON template (path or - to supply through stdin)",
    required=True,
    type=click.File("r"),
)
@click.option(
    "--parameter",
    default=[],
    type=RosParameterType(),
    multiple=True,
    help="Comma-separated list of key=val parameters to set in the template",
)
@click.option(
    "--timeout-mins",
    default=10,
    help="Timeout if stack was not created within specified minutes",
)
@click.option(
    "--disabled-rollback/--no-disabled-rollback",
    default=True,
    is_flag=True,
    help="on failure",
)
@click.pass_obj
def update_stack(obj, name, template, parameter, timeout_mins, disabled_rollback):
    """Updates a ROS stack"""
    stack = _find_stack_by_name(obj["client"], name)
    body = load_template(template)
    request = UpdateStackRequest.UpdateStackRequest()
    request.set_StackId(stack["Id"])
    request.set_StackName(name)
    request_body = {
        "Name": name,
        "TimeoutMins": timeout_mins,
        "Template": body,
        "Parameters": {p.name: p.value for p in parameter},
        "DisabledRollback": disabled_rollback,
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
    """Get details of a single stack"""
    stack = _find_stack_by_name(obj["client"], name)

    request = DescribeStackDetailRequest.DescribeStackDetailRequest()
    request.add_path_param("StackName", name)
    request.add_path_param("StackId", stack["Id"])

    client = obj["client"]
    response = client.do_action_with_exception(request)

    output_json(response)


@ros.command()
@click.option("--name", help="Stack name", required=True)
@click.pass_obj
def describe_resources(obj, name):
    """List the resources in a given stack"""
    stack = _find_stack_by_name(obj["client"], name)

    request = DescribeResourcesRequest.DescribeResourcesRequest()
    request.set_StackId(stack["Id"])
    request.set_StackName(name)

    client = obj["client"]
    response = client.do_action_with_exception(request)

    output_json(response)


def _find_stack_by_name(client, name):
    stacks_request = DescribeStacksRequest.DescribeStacksRequest()

    stacks_response = json.loads(client.do_action_with_exception(stacks_request))
    stacks = list(filter(lambda s: s["Name"] == name, stacks_response["Stacks"]))
    if len(stacks) == 0:
        raise Exception("Could not find the '%s' stack" % name)

    return stacks[0]
