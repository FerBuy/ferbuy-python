import sys
import textwrap

from ferbuy import errors

# Requests is the prefered HTTP library
# Fall back to urllib2 or urllib.request depending on Python version

try:
    import urllib.request
except ImportError:
    import urllib2

try:
    import requests
except ImportError:
    requests = None


def new_client(*args, **kwargs):
    if requests:
        client = RequestsClient
    elif sys.version_info >= (3, 0):
        client = Urllib3Client
    else:
        client = Urllib2Client
    return client(*args, **kwargs)


class HTTPClient(object):

    def request(self, method, url, headers, data=None):
        raise NotImplementedError('HTTPClient subclasses must '
                                  'implement "request" method')


class RequestsClient(HTTPClient):

    name = 'requests'

    def request(self, method, url, headers, data=None):
        try:
            result = requests.request(
                method, url, headers=headers, data=data, timeout=80)

            content = result.content
            status_code = result.status_code
        except requests.exceptions.HTTPError as e:
            content = result.content
            status_code = result.status_code
        except Exception as e:
            self.handle_error(e)
        return content, status_code

    def handle_error(self, e):
        if isinstance(e, requests.exceptions.RequestException):
            msg = ("Unexpected error communicating with FerBuy. "
                   "If this problem persists, let us know at "
                   "support@ferbuy.com.")
        else:
            msg = ("Unexpected error communicating with FerBuy. "
                   "It looks like there's probably a configuration "
                   "issue locally. If this problem persists, let us know at "
                   "support@ferbuy.com.")
        err = "{0}: {1}".format(e.__class__.__name__, e)
        msg = textwrap.fill(msg + "\n\n(Network error: {0})".format(err))
        raise errors.APIConnectionError(msg)


class Urllib2Client(HTTPClient):

    name = 'urllib2'

    def request(self, method, url, headers, data=None):
        req = urllib2.Request(url, data, headers)
        req.get_method = lambda: method.upper()

        try:
            result = urllib2.urlopen(req)
            content = result.read()
            status_code = result.code
        except urllib2.HTTPError as e:
            content = result.read()
            status_code = result.code
        except (ValueError, urllib2.URLError) as e:
            self.handle_error(e)
        return content, status_code

    def handle_error(self, e):
        msg = ("Unexpected error communicating with FerBuy. "
               "If this problem persists, let us know at "
               "support@ferbuy.com.")
        err = "{0}: {1}".format(e.__class__.__name__, e)
        msg = textwrap.fill(msg + "\n\n(Network error: {0})".format(err))
        raise errors.APIConnectionError(msg)


class Urllib3Client(HTTPClient):

    name = 'urllib.request'

    def request(self, method, url, headers, data=None):

        req = urllib.request.Request(url, data, headers)
        req.get_method = lambda: method.upper()

        try:
            result = urllib.request.urlopen(req)
            content = result.read()
            status_code = result.code
        except urllib.error.URLError as e:
            content = result.read()
            status_code = result.code
        except (ValueError, urllib.request.URLError) as e:
            self.handle_error(e)
        return content, status_code

    def handle_error(self, e):
        msg = ("Unexpected error communicating with FerBuy. "
               "If this problem persists, let us know at "
               "support@ferbuy.com.")
        err = "{0}: {1}".format(e.__class__.__name__, e)
        msg = textwrap.fill(msg + "\n\n(Network error: {0})".format(err))
        raise errors.APIConnectionError(msg)
