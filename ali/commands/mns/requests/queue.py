from ali.commands.mns.requests.base_request import BaseRequest
from ali.commands.mns.util import bytes_to_b64


class CreateQueueRequest(BaseRequest):
    def __init__(
        self,
        queue_name,
        delay_seconds=0,
        maximum_message_size=65536,
        message_retention_period=345600,
        visibility_timeout=30,
        polling_wait_seconds=0,
    ):
        super().__init__(
            path="/queues/%s" % queue_name,
            method="PUT",
            body_params={
                "DelaySeconds": delay_seconds,
                "MaximumMessageSize": maximum_message_size,
                "MessageRetentionPeriod": message_retention_period,
                "VisibilityTimeout": visibility_timeout,
                "PollingWaitSeconds": polling_wait_seconds,
            },
            root_el="Queue",
        )


class ListQueueRequest(BaseRequest):
    def __init__(self, marker=None, num=1000, prefix=None):
        mns_headers = {}
        if marker:
            mns_headers["x-mns-marker"] = str(marker)

        mns_headers["x-mns-ret-number"] = str(num)
        if prefix:
            mns_headers["x-mns-prefix"] = str(prefix)

        super().__init__(path="/queues", method="GET", mns_headers=mns_headers)


class GetQueueAttributesRequest(BaseRequest):
    def __init__(self, queue_name):
        super().__init__(path="/queues/%s" % queue_name, method="GET")


class DeleteQueueRequest(BaseRequest):
    def __init__(self, queue_name):
        super().__init__(path="/queues/%s" % queue_name, method="DELETE")


class SendMessageRequest(BaseRequest):
    def __init__(self, queue_name, message_body, delay_seconds=0, priority=8):
        super().__init__(
            path="/queues/%s/messages" % queue_name,
            method="POST",
            body_params={
                "MessageBody": bytes_to_b64(bytes(message_body, "UTF-8")),
                "DelaySeconds": delay_seconds,
                "Priority": priority,
            },
            root_el="Message",
        )


class ReceiveMessageRequest(BaseRequest):
    def __init__(self, queue_name, wait_seconds=10):
        super().__init__(
            path="/queues/%s/messages?waitseconds=%s" % (queue_name, wait_seconds),
            method="GET",
        )


class BatchReceiveMessageRequest(BaseRequest):
    def __init__(self, queue_name, num_of_messages=16, wait_seconds=10):
        super().__init__(
            path="/queues/%s/messages?numOfMessages=%s&waitseconds=%s"
            % (queue_name, num_of_messages, wait_seconds),
            method="GET",
        )


class PeekMessageRequest(BaseRequest):
    def __init__(self, queue_name):
        super().__init__(
            path="/queues/%s/messages?peekonly=true" % queue_name, method="GET"
        )


class BatchPeekMessageRequest(BaseRequest):
    def __init__(self, queue_name, num_of_messages=16):
        super().__init__(
            path="/queues/%s/messages?peekonly=true&numOfMessages=%s"
            % (queue_name, num_of_messages),
            method="GET",
        )


class DeleteMessageRequest(BaseRequest):
    def __init__(self, queue_name, receipt_handle):
        super().__init__(
            path="/queues/%s/messages?ReceiptHandle=%s" % (queue_name, receipt_handle),
            method="DELETE",
        )
