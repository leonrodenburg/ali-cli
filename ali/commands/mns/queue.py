import json

import click
import xmltodict
from aliyunsdksts.request.v20150401 import GetCallerIdentityRequest

from ali.commands.mns.client import MnsClient
from ali.commands.mns.requests.queue import (
    BatchPeekMessageRequest,
    BatchReceiveMessageRequest,
    CreateQueueRequest,
    DeleteMessageRequest,
    DeleteQueueRequest,
    GetQueueAttributesRequest,
    ListQueueRequest,
    PeekMessageRequest,
    ReceiveMessageRequest,
    SendMessageRequest,
)
from ali.helpers.output import output_json, output_success, output_error


@click.group()
def queue():
    """Queue commands"""
    pass


@queue.command()
@click.option("--name", help="Queue name", required=True)
@click.option(
    "--delay-seconds",
    help="Amount of time before messages become visible (in seconds, max. 7 days)",
    default=0,
    required=False,
)
@click.option(
    "--maximum-message-size",
    help="Maximum body size of a message (in bytes, min. 1024)",
    default=65536,
    required=False,
)
@click.option(
    "--message-retention-period",
    help="Retention period of messages on the queue (in seconds, between 60 and 1296000 = 15 days)",
    default=345600,
    required=False,
)
@click.option(
    "--visibility-timeout",
    help="Time a message stays off the queue when it was received (in seconds, between 1 and 43200 = 12 hours)",
    default=30,
    required=False,
)
@click.option(
    "--polling-wait-seconds",
    help="Determines how long consumers can wait when there are no messages (in seconds, between 0 and 30)",
    default=0,
    required=False,
)
@click.pass_obj
def create(
    obj,
    name,
    delay_seconds,
    maximum_message_size,
    message_retention_period,
    visibility_timeout,
    polling_wait_seconds,
):
    """Create a queue"""
    request = CreateQueueRequest(
        name,
        delay_seconds=delay_seconds,
        maximum_message_size=maximum_message_size,
        message_retention_period=message_retention_period,
        visibility_timeout=visibility_timeout,
        polling_wait_seconds=polling_wait_seconds,
    )
    mns_client = _get_mns_client(obj["client"])
    response = mns_client.call_sync(request)

    if response.status_code == 201 or response.status_code == 204:
        output_success("Queue '%s' created successfully" % name)
        output_json(json.dumps({"QueueUrl": response.headers["Location"]}))
    else:
        print(response)
        output_error("Queue creation failed")
        output_json(_xml_to_json_str(response.text))


@queue.command()
@click.option("--marker", help="Page marker to start paging from", required=False)
@click.option("--num", help="Number of items to return", default=1000, required=False)
@click.option("--prefix", help="Prefix to filter queues on", required=False)
@click.pass_obj
def list(obj, marker, num, prefix):
    """Return a list of queues"""
    request = ListQueueRequest(marker, num, prefix)
    mns_client = _get_mns_client(obj["client"])
    response = mns_client.call_sync(request)
    output_json(_xml_to_json_str(response.text))


@queue.command()
@click.option("--name", help="Queue name", required=True)
@click.pass_obj
def get(obj, name):
    """Get the attributes of a single queue"""
    request = GetQueueAttributesRequest(name)
    mns_client = _get_mns_client(obj["client"])
    response = mns_client.call_sync(request)
    output_json(_xml_to_json_str(response.text))


@queue.command()
@click.option("--name", help="Queue name", required=True)
@click.pass_obj
def delete(obj, name):
    """Delete a queue"""
    request = DeleteQueueRequest(name)
    mns_client = _get_mns_client(obj["client"])
    response = mns_client.call_sync(request)

    if response.status_code == 204:
        output_success("Queue '%s' deleted successfully" % name)
    else:
        output_error("Queue deletion failed (status code: %s)" % response.status_code)


@queue.command()
@click.option("--name", help="Queue name", required=True)
@click.option(
    "--message-body",
    help="Raw message file (path or - to supply through stdin)",
    required=True,
    type=click.File("r"),
)
@click.pass_obj
def send_message(obj, name, message_body):
    """Put a message on a queue"""
    message_contents = message_body.read()
    request = SendMessageRequest(name, message_contents)
    mns_client = _get_mns_client(obj["client"])
    response = mns_client.call_sync(request)

    if response.status_code == 201:
        output_success("Message sent successfully")
    else:
        output_error("Could not send message")

    output_json(_xml_to_json_str(response.text))


@queue.command()
@click.option("--name", help="Queue name", required=True)
@click.option(
    "--wait-seconds",
    help="Amount of time to wait (long-poll), in seconds",
    default=10,
    required=False,
)
@click.pass_obj
def receive_message(obj, name, wait_seconds):
    """Receive a single message"""
    request = ReceiveMessageRequest(name, wait_seconds=wait_seconds)
    mns_client = _get_mns_client(obj["client"])
    response = mns_client.call_sync(request)
    output_json(_xml_to_json_str(response.text))


@queue.command()
@click.option("--name", help="Queue name", required=True)
@click.option(
    "--num-of-messages", help="Number of messages", default=16, required=False
)
@click.option(
    "--wait-seconds",
    help="Amount of time to wait (long-poll), in seconds",
    default=10,
    required=False,
)
@click.pass_obj
def receive_messages(obj, name, num_of_messages, wait_seconds):
    """Receive multiple messages in a batch"""
    request = BatchReceiveMessageRequest(
        name, num_of_messages=num_of_messages, wait_seconds=wait_seconds
    )
    mns_client = _get_mns_client(obj["client"])
    response = mns_client.call_sync(request)
    output_json(_xml_to_json_str(response.text))


@queue.command()
@click.option("--name", help="Queue name", required=True)
@click.pass_obj
def peek_message(obj, name):
    """Peek at a single message, without changing message status"""
    request = PeekMessageRequest(name)
    mns_client = _get_mns_client(obj["client"])
    response = mns_client.call_sync(request)
    output_json(_xml_to_json_str(response.text))


@queue.command()
@click.option("--name", help="Queue name", required=True)
@click.option(
    "--num-of-messages", help="Number of messages", default=16, required=False
)
@click.pass_obj
def peek_messages(obj, name, num_of_messages):
    """Peek at a batch of messages, without changing message status"""
    request = BatchPeekMessageRequest(name, num_of_messages=num_of_messages)
    mns_client = _get_mns_client(obj["client"])
    response = mns_client.call_sync(request)
    output_json(_xml_to_json_str(response.text))


@queue.command()
@click.option("--name", help="Queue name", required=True)
@click.option("--handle", help="Message receipt handle", required=True)
@click.pass_obj
def delete_message(obj, name, handle):
    """Remove a message from the queue (acknowledge it)"""
    request = DeleteMessageRequest(name, handle)
    mns_client = _get_mns_client(obj["client"])
    response = mns_client.call_sync(request)

    if response.status_code == 204:
        output_success("Message deleted successfully")
    else:
        output_error("Could not delete message from queue")
        output_json(_xml_to_json_str(response.text))


def _get_mns_client(client):
    account_id = _resolve_account_id(client)
    return MnsClient(
        account_id,
        client.get_access_key(),
        client.get_access_secret(),
        client.get_region_id(),
    )


def _resolve_account_id(client):
    request = GetCallerIdentityRequest.GetCallerIdentityRequest()
    response = json.loads(client.do_action_with_exception(request))
    return response["AccountId"]


def _xml_to_json_str(xml):
    return json.dumps(xmltodict.parse(xml))
