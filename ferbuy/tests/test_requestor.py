import unittest

from mock import Mock

import ferbuy
from .utils import FerbuyUnitTestCase

VALID_API_METHODS = ('get', 'post')


class MatchHeaders(object):

    EXPECTED_HEADERS = ['X-FerBuy-Client-User-Agent', 'User-Agent']

    METHOD_SPECIFIC_HEADERS = {'post': ['Content-Type']}

    def __init__(self, site_id=None, secret=None,
                 extra={}, request_method=None):

        self.request_method = request_method
        self.site_id = site_id or ferbuy.site_id
        self.secret = secret or ferbuy.secret
        self.extra = extra

    def __eq__(self, other):
        return (self._match_keys(other) and
                self._match_extra(other))

    def _match_keys(self, other):
        expected_keys = self.EXPECTED_HEADERS + self.extra.keys()

        if (self.request_method is not None
                and self.request_method in self.METHOD_SPECIFIC_HEADERS):
            extra_header = self.METHOD_SPECIFIC_HEADERS[self.request_method]
            expected_keys.extend(extra_header)

        return (sorted(other.keys()) == sorted(expected_keys))

    def _match_extra(self, other):
        for key, value in self.extra.items():
            if other[key] != value:
                return False
        return True


class APIRequestorTests(FerbuyUnitTestCase):

    def setUp(self):
        super(APIRequestorTests, self).setUp()

        self.http_client = Mock(ferbuy.http_client.HTTPClient)
        self.http_client.name = 'mockclient'

        self.requestor = ferbuy.api_requestor.APIRequestor(
            site_id=1000,
            secret='dummy secret',
            client=self.http_client)

    def valid_url(self, path='/dummy'):
        return 'https://gateway.ferbuy.com/api{0}'.format(path)

    @property
    def valid_path(self):
        return '/dummy'

    def mock_response(self, response, status_code, requestor=None):
        if not requestor:
            requestor = self.requestor

        requestor.client.request = Mock(return_value=(response, status_code))

    def check_call(self, method, abs_url=None, headers=None,
                   post_data=None, requestor=None):
        if not abs_url:
            abs_url = self.valid_url()
        if not requestor:
            requestor = self.requestor
        if not headers:
            headers = MatchHeaders(request_method=method)

        self.requestor.client.request.assert_called_with(
            method, abs_url, headers, post_data)

    def test_singleton(self):
        a = ferbuy.api_requestor.APIRequestor()
        b = ferbuy.api_requestor.APIRequestor()
        self.assertEqual(a, b)

    def test_site_id_missing(self):
        self.mock_response(
            '{"error":{"errorSubject":"Merchant error",'
            '"errorDetail":"The variable site_id is not set correctly"}}',
            500)

        with self.assertRaises(ferbuy.errors.APIError):
            self.requestor.request('post', self.valid_path, {})

    def test_empty_response(self):
        for method in VALID_API_METHODS:
            self.mock_response('{}', 500)

            with self.assertRaises(ferbuy.errors.APIError):
                response, status_code = self.requestor.request(
                    method, self.valid_path, {})

    def test_uses_headers(self):
        self.mock_response('{"api": {}}', 200)
        self.requestor.request('get', self.valid_path, {}, {'foo': 'bar'})
        self.check_call('get', headers=MatchHeaders(extra={'foo': 'bar'}))

    def test_invalid_method(self):
        self.mock_response('{"api": {}}', 200)

        with self.assertRaises(ferbuy.errors.APIConnectionError):
            self.requestor.request('dummy', self.valid_path, {})

    def test_server_error(self):
        self.mock_response('{"api": {}}', 500)

        with self.assertRaises(ferbuy.errors.APIError):
            self.requestor.request('post', self.valid_path, {})

    def test_invalid_request_error(self):
        self.mock_response('{"api": {}}', 400)

        with self.assertRaises(ferbuy.errors.InvalidRequestError):
            self.requestor.request('post', self.valid_path, {})

    def test_valid_response(self):
        self.mock_response(
            '{"api":{"response":{"code":200,'
            '"message":"Transaction ID 1000 marked as shipped"}}}',
            200)

        req = self.requestor.request(
            'post', self.valid_path, {})

        self.assertEqual(req.response.code, 200)
        self.assertEqual(req.response.message,
                         "Transaction ID 1000 marked as shipped")


if __name__ == '__main__':
    unittest.main()
