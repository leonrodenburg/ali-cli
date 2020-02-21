import json

import oss2
import requests
from aliyunsdkcore.auth.credentials import (
    AccessKeyCredential,
    StsTokenCredential,
    RamRoleArnCredential,
    EcsRamRoleCredential,
)
from aliyunsdksts.request.v20150401 import AssumeRoleRequest


def get_bucket(bucket_name, context):
    credentials = context["credentials"]
    if isinstance(credentials, AccessKeyCredential):
        access_key_id = credentials.access_key_id
        access_key_secret = credentials.access_key_secret
        auth = oss2.Auth(access_key_id, access_key_secret)
    elif isinstance(credentials, StsTokenCredential):
        access_key_id = credentials.sts_access_key_id
        access_key_secret = credentials.sts_access_key_secret
        sts_token = credentials.sts_token
        auth = oss2.StsAuth(access_key_id, access_key_secret, sts_token)
    elif isinstance(credentials, RamRoleArnCredential):
        assume_role_request = AssumeRoleRequest.AssumeRoleRequest()
        assume_role_request.set_RoleArn(credentials.role_arn)
        assume_role_request.set_RoleSessionName(credentials.session_role_name)
        response = json.loads(
            context["client"].do_action_with_exception(assume_role_request)
        )
        assumed_creds = response["Credentials"]
        auth = oss2.StsAuth(
            assumed_creds["AccessKeyId"],
            assumed_creds["AccessKeySecret"],
            assumed_creds["SecurityToken"],
        )
    elif isinstance(credentials, EcsRamRoleCredential):
        url = (
            "http://100.100.100.200/latest/meta-data/ram/security-credentials/%s"
            % credentials.role_name
        )
        response = requests.get(url).json()
        if response["Code"] != "Success":
            raise Exception(
                "Unable to have ECS instance assume role: '%s'" % credentials.role_name
            )
        auth = oss2.StsAuth(
            response["AccessKeyId"],
            response["AccessKeySecret"],
            response["SecurityToken"],
        )
    else:
        raise Exception(
            "Credentials could not be wired into OSS client (type: '%s')"
            % type(credentials)
        )

    return oss2.Bucket(
        auth, "http://oss-%s.aliyuncs.com" % context["region_id"], bucket_name
    )
