import base64
import hashlib
import re


def str_to_md5(string):
    return hashlib.md5(bytes(string, "UTF-8")).hexdigest()


def bytes_to_b64(b):
    b64 = base64.b64encode(b)
    return str(b64, "UTF-8").strip()


def strip_protocol(url):
    pattern = re.compile(r"[a-zA-Z-]+\:\/\/")
    return pattern.sub("", url)
