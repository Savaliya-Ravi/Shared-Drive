import logging
import traceback

import getmac

from Middleware.request_middleware import request_var


class SourceFilter(logging.Filter):
    def __init__(self, default_source="default_source"):
        super().__init__()
        self.default_source = default_source

    def filter(self, record):
        try:
            request = request_var.get()
            record.source = request.headers.get('source', '-')
            return True
        except LookupError:
            traceback.print_exc()
            record.source = self.default_source


class IPMACFilter(logging.Filter):
    def __init__(self, default_source="default_source"):
        super().__init__()
        self.default_source = default_source

    def filter(self, record):
        try:
            request = request_var.get()
            record.mac_address = getmac.get_mac_address(ip=request.client.host)
            record.ip_address = request.client.host
            return True
        except LookupError:
            traceback.print_exc()
            record.ip_address = self.default_source
            record.mac_address = self.default_source
