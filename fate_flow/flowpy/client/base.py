#
#  Copyright 2019 The FATE Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
import sys
import json
import inspect
import requests
import traceback
from fate_flow.flowpy.client.api.base import BaseFlowAPI


def _is_api_endpoint(obj):
    return isinstance(obj, BaseFlowAPI)


class BaseFlowClient:
    API_BASE_URL = ''

    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls)
        api_endpoints = inspect.getmembers(self, _is_api_endpoint)
        for name, api in api_endpoints:
            print('name: {}, api: {}'.format(name, api))
            api_cls = type(api)
            api = api_cls(self)
            setattr(self, name, api)
        return self

    def __init__(self, ip, port, version):
        self._http = requests.Session()
        self.ip = ip
        self.port = port
        self.version = version

    def _request(self, method, url, echo, **kwargs):
        request_url = self.API_BASE_URL + url
        try:
            response = self._http.request(method=method, url=request_url, **kwargs)
        except Exception as e:
            exc_type, exc_value, exc_traceback_obj = sys.exc_info()
            response = {'retcode': 100, 'retmsg': str(e),
                        'traceback': traceback.format_exception(exc_type, exc_value, exc_traceback_obj)}
            if 'Connection refused' in str(e):
                response['retmsg'] = 'Connection refused, Please check if the fate flow service is started'
                del response['traceback']
            if echo:
                print(self._handle_result(response))
                return
            return response
        else:
            if echo:
                print(self._handle_result(response))
                return
            return response

    @staticmethod
    def _decode_result(response):
        try:
            result = json.loads(response.content.decode('utf-8', 'ignore'), strict=False)
        except (TypeError, ValueError):
            return response
        else:
            return result

    def _handle_result(self, response):
        if not isinstance(response, dict):
            result = self._decode_result(response)
        else:
            result = response
        return json.dumps(result, indent=4, ensure_ascii=False)

    def get(self, url, echo, **kwargs):
        return self._request(method='get', url=url, echo=echo, **kwargs)

    def post(self, url, echo, **kwargs):
        return self._request(method='post', url=url, echo=echo, **kwargs)
