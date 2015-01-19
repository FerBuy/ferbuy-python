import datetime
import random
import sys
import unittest

from mock import patch, Mock

import ferbuy


NOW = datetime.datetime.now()

DUMMY_REFUND = {
    'transaction_id': random.randint(1000, 9999),
    'amount': 100,
    'currency': 'eur'
}

DUMMY_SHIPPMENT = {
    'transaction_id': random.randint(1000, 9999),
    'courier': 'DHL',
    'tracking_number': random.randint(1000, 9999),
}

DUMMY_DELIVERY = {
    'transaction_id': random.randint(1000, 9999),
    'date': NOW,
}


class FerbuyTestCase(unittest.TestCase):

    RECOVER_ATTRS = ['site_id', 'secret', 'env']

    def setUp(self):
        super(FerbuyTestCase, self).setUp()

        self._original_atts = {}
        for attr in self.RECOVER_ATTRS:
            self._original_atts[attr] = getattr(ferbuy, attr)

    def tearDown(self):
        super(FerbuyTestCase, self).setUp()

        for attr in self.RECOVER_ATTRS:
            setattr(ferbuy, attr, self._original_atts[attr])


class FerbuyUnitTestCase(FerbuyTestCase):

    HTTP_LIBS = ['requests']

    if sys.version_info >= (3, 0):
        HTTP_LIBS.append('urllib.request')
    else:
        HTTP_LIBS.append('urllib2')

    def setUp(self):
        super(FerbuyUnitTestCase, self).setUp()

        self.request_patchers = {}
        self.request_mocks = {}

        for lib in self.HTTP_LIBS:
            patcher = patch("ferbuy.http_client.{0}".format(lib))
            self.request_mocks[lib] = patcher.start()
            self.request_patchers[lib] = patcher

    def tearDown(self):
        super(FerbuyUnitTestCase, self).setUp()

        for patcher in self.request_patchers.values():
            patcher.stop()


class FerbuyApiTestCase(FerbuyTestCase):

    def setUp(self):
        super(FerbuyTestCase, self).setUp()

        self.requestor_patcher = patch('ferbuy.api_requestor.APIRequestor')
        requestor_class_mock = self.requestor_patcher.start()
        self.requestor_mock = requestor_class_mock.return_value

    def tearDown(self):
        super(FerbuyTestCase, self).tearDown()
        self.requestor_patcher.stop()

    def mock_response(self, response):
        self.requestor_mock.request = Mock(return_value=(response,
                                                         'status_code'))
