from email.utils import formatdate


class BaseRequest:
    def __init__(self, path, method, body_params={}, root_el=None, mns_headers={}):
        self._path = path
        self._method = method
        self._body_params = body_params
        self._root_el = root_el
        self._date = formatdate(timeval=None, localtime=False, usegmt=True)
        self._mns_headers = {"x-mns-version": "2015-06-06", **mns_headers}

    def get_path(self):
        return self._path

    def get_method(self):
        return self._method

    def get_date(self):
        return self._date

    def get_headers(self):
        return {"Date": self._date, "Content-Type": "application/xml"}

    def get_mns_headers(self):
        return self._mns_headers

    def has_body(self):
        return self._body_params

    def get_body_params(self):
        return self._body_params

    def get_body_xml(self):
        return (
            (
                '<?xml version="1.0" encoding="UTF-8"?><%s xmlns="http://mns.aliyuncs.com/doc/v1/">%s</%s>'
                % (self._root_el, self._to_xml_params(self._body_params), self._root_el)
            )
            if self._body_params
            else ""
        )

    def _to_xml_params(self, params):
        xml_params = ["<%s>%s</%s>" % (key, val, key) for key, val in params.items()]
        return "".join(xml_params)
