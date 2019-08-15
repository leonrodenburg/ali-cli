import hashlib
import hmac

import requests

from ali.commands.mns.requests.base_request import BaseRequest
from ali.commands.mns.util import str_to_md5, strip_protocol, bytes_to_b64


class MnsClient:
    def __init__(
        self,
        account_id: str,
        access_key_id: str,
        access_key_secret: str,
        region_id: str,
    ):
        self._endpoint = "https://%s.mns.%s.aliyuncs.com" % (account_id, region_id)
        self._access_key_id = access_key_id
        self._access_key_secret = access_key_secret

    def call_sync(self, request: BaseRequest):
        auth_header = "MNS %s:%s" % (self._access_key_id, self._sign_request(request))
        headers = {
            **request.get_headers(),
            "Authorization": auth_header,
            "Host": strip_protocol(self._endpoint),
            **request.get_mns_headers(),
        }

        if request.has_body():
            headers["Content-MD5"] = bytes_to_b64(
                bytes(str_to_md5(request.get_body_xml()), "UTF-8")
            )

        response = requests.request(
            request.get_method(),
            "%s%s" % (self._endpoint, request.get_path()),
            headers=headers,
            data=request.get_body_xml(),
        )

        return response

    def _sign_request(self, request: BaseRequest):
        # See https://help.aliyun.com/document_detail/27487.html?spm=a2c4g.11186623.6.679.40333230D6nCld
        # Create string to hash
        raw_signature = ""
        raw_signature += request.get_method() + "\n"  # HTTP method
        raw_signature += (
            (bytes_to_b64(bytes(str_to_md5(request.get_body_xml()), "UTF-8")) + "\n")
            if request.has_body()
            else "\n"
        )  # Content MD5
        raw_signature += "application/xml" + "\n"  # Content type
        raw_signature += request.get_date() + "\n"  # Date

        for key, val in iter(sorted(request.get_mns_headers().items())):
            raw_signature += "%s:%s\n" % (key, val)  # CanonicalizedMNSHeaders

        raw_signature += request.get_path()  # CanonicalizedResource

        # Get raw bytes
        key = bytes(self._access_key_secret, "UTF-8")
        message = bytes(raw_signature, "UTF-8")

        # Perform HMAC-SHA1 with access key secret as key and raw signature as message
        digester = hmac.new(key, message, hashlib.sha1)
        signature_digest = digester.digest()

        # Base64 encode the result
        return bytes_to_b64(signature_digest)
