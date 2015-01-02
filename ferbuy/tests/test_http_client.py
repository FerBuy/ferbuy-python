import sys
import unittest
from mock import Mock

import ferbuy
from .utils import FerbuyUnitTestCase

VALID_API_METHODS = ('get', 'post')


class HttpClientTests(FerbuyUnitTestCase):

    def check_default(self, none_libs, expected):
        for lib in none_libs:
            setattr(ferbuy.http_client, lib, None)

        client = ferbuy.http_client.new_client()
        self.assertTrue(isinstance(client, expected))

    def test_default_http_client_requests(self):
        self.check_default([], ferbuy.http_client.RequestsClient)

    def test_default_http_client_urllib(self):
        if sys.version_info >= (3, 0):
            self.check_default(['requests'], ferbuy.http_client.Urllib3Client)
        else:
            self.check_default(['requests'], ferbuy.http_client.Urllib2Client)


class ClientTestBase(object):

    @property
    def request_mock(self):
        return self.request_mocks[self.request_client.name]

    def valid_url(self, path='/dummy'):
        return 'https://gateway.ferbuy.com/api{0}'.format(path)

    def make_request(self, method, url, headers, data):
        client = self.request_client()
        return client.request(method, url, headers, data)

    def mock_response(self, body, code):
        raise NotImplementedError(
            "You must implement this in your test subclass")

    def mock_error(self, error):
        raise NotImplementedError(
            "You must implement this in your test subclass")

    def check_call(self, method, abs_url, headers, params):
        raise NotImplementedError(
            "You must implement this in your test subclass")

    def test_request(self):
        self.mock_response(self.request_mock, '{"foo": "bar"}', 200)

        for method in VALID_API_METHODS:
            abs_url = self.valid_url()
            data = ''

            if method not in ('post', 'put'):
                abs_url = '{0}?{1}&output_type=json'.format(abs_url, data)
                data = None

            headers = {'dummy-header': 'dummy header value'}
            body, code = self.make_request(method, abs_url, headers, data)

            self.assertEqual(200, code)
            self.assertEqual('{"foo": "bar"}', body)

            self.check_call(self.request_mock,
                            method, abs_url,
                            data, headers)

    def test_exception(self):
        self.mock_error(self.request_mock)
        with self.assertRaises(ferbuy.errors.APIConnectionError):
            self.make_request('get', self.valid_url(), {}, None)


class RequestsClientTests(FerbuyUnitTestCase, ClientTestBase):

    request_client = ferbuy.http_client.RequestsClient

    def mock_response(self, mock, body, code):
        result = Mock()
        result.content = body
        result.status_code = code
        mock.request = Mock(return_value=result)

    def mock_error(self, mock):
        mock.exceptions.RequestException = Exception
        mock.request.side_effect = mock.exceptions.RequestException()

    def check_call(self, mock, method, url, post_data, headers):
        mock.request.assert_called_with(method, url,
                                        headers=headers,
                                        data=post_data,
                                        timeout=80)


class UrllibClientTests(FerbuyUnitTestCase, ClientTestBase):

    if sys.version_info >= (3, 0):
        request_client = ferbuy.http_client.Urllib3Client
    else:
        request_client = ferbuy.http_client.Urllib2Client

    def mock_response(self, mock, body, code):
        response = Mock
        response.read = Mock(return_value=body)
        response.code = code

        self.request_object = Mock()
        mock.Request = Mock(return_value=self.request_object)

        mock.urlopen = Mock(return_value=response)

    def mock_error(self, mock):
        mock.URLError = Exception
        mock.urlopen.side_effect = mock.URLError()

    def check_call(self, mock, meth, url, post_data, headers):
        mock.Request.assert_called_with(url, post_data, headers)
        mock.urlopen.assert_called_with(self.request_object)


if __name__ == '__main__':
    unittest.main()
