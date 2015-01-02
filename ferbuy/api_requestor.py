import ferbuy
import hashlib
import platform
import urllib

from ferbuy import errors
from ferbuy import utils
from ferbuy import version
from ferbuy.http_client import new_client
from ferbuy.utils import Singleton


class FerbuyObject(dict):

    def __init__(self, d=None, **kwargs):
        if d is None:
            d = {}

        if kwargs:
            d.update(**kwargs)

        for k, v in d.items():
            setattr(self, k, v)

        for k in self.__class__.__dict__.keys():
            if not (k.startswith('__') and k.endswith('__')):
                setattr(self, k, getattr(self, k))

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as e:
            raise AttributeError(*e.args)

    def __setattr__(self, name, value):
        if isinstance(value, (list, tuple)):
            value = [self.__class__(x)
                     if isinstance(x, dict) else x for x in value]
        else:
            value = self.__class__(value) if isinstance(value, dict) else value

        super(FerbuyObject, self).__setattr__(name, value)
        self[name] = value


class APIRequestor(Singleton):

    def __init__(self, site_id=None, api_secret=None,
                 api_base=None, client=None):

        if site_id:
            self.site_id = site_id
        else:
            self.site_id = ferbuy.site_id

        if api_secret:
            self.api_secret = api_secret
        else:
            self.api_secret = ferbuy.api_secret

        if api_base:
            self.api_base = api_base
        else:
            self.api_base = ferbuy.api_base

        self.__client = client or new_client()

    @property
    def client(self):
        return self.__client

    def sign(self, transaction_id, command, output_type, **kwargs):
        signature = "&".join([
            str(self.site_id), str(transaction_id),
            command, output_type, str(self.api_secret)
        ])
        hash = hashlib.sha1(signature)
        return hash.hexdigest()

    def request(self, method, url, data=None, headers=None):
        response, status_code = self.api_call(
            method.lower(), url, data, headers)
        result = self.process_response(response, status_code)
        return result

    def api_call(self, method, url, data, supplied_headers):
        abs_url = '{0}{1}'.format(self.api_base, url)

        if method in ('get', 'delete'):
            post_data = None
        elif method in ('post', 'put'):
            post_data = urllib.urlencode(data)
        else:
            raise errors.APIConnectionError(
                "Unrecognized HTTP method {0}. This may indicate a bug in the "
                "FerBuy Python library.".format(method))

        add_info = {
            'bindings_version': version.VERSION,
            'lang': 'Python',
            'lang_version': platform.python_version(),
            'platform': platform.platform()
        }

        headers = {
            'X-FerBuy-Client-User-Agent': utils.json.dumps(add_info),
            'User-Agent': 'FerBug/v1 PythonBinding/{0}'.format(version.VERSION),
        }

        if method == 'post':
            headers['Content-Type'] = 'application/x-www-form-urlencoded'

        if supplied_headers is not None:
            for key, value in supplied_headers.items():
                headers[key] = value

        response, status_code = self.client.request(
            method, abs_url, headers, post_data)

        utils.logger.info(
            "Calling API resource at {0} returned (status code, response) of "
            "({1}, {2})".format(abs_url, status_code, response))

        return response, status_code

    def process_response(self, response, status_code):
        try:
            resp_dict = utils.json.loads(response)
            obj = FerbuyObject(resp_dict['api'])
        except (KeyError, TypeError):
            obj = FerbuyObject(resp_dict.get('error', None))
            if obj:
                raise errors.APIError("{0}. {1}".format(obj.errorSubject,
                                                        obj.errorDetail))
            else:
                raise errors.APIError("Invalid response object from API")

        if not(200 <= status_code <= 300):
            self.handle_error(response, status_code)
        return obj

    def handle_error(self, response, status_code):
        if status_code in (400, 401):
            raise errors.InvalidRequestError(
                "Invalid request error", response, status_code)
        else:
            raise errors.APIError(
                "API request error", response, status_code)
