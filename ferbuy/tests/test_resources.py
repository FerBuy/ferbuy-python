import datetime
import unittest

from mock import Mock

import ferbuy
from .utils import FerbuyUnitTestCase

VALID_API_METHODS = ('get', 'post')


class ResourceTests(FerbuyUnitTestCase):

    def setUp(self):
        super(ResourceTests, self).setUp()

        self.http_client = Mock(ferbuy.http_client.HTTPClient)
        self.http_client.name = 'mockclient'

        self.requestor = ferbuy.api_requestor.APIRequestor(
            site_id=1000,
            api_secret='dummy secret',
            client=self.http_client)

    @property
    def valid_path(self):
        return '/dummy'

    def mock_response(self, response, status_code, requestor=None):
        if not requestor:
            requestor = self.requestor

        requestor.client.request = Mock(return_value=(response, status_code))


class TransactionResourceTests(ResourceTests):

    def test_valid_refund(self):
        self.mock_response("""
        {"api":{
          "request":{"command":"EUR100","site_id":1000,"transaction_id":10001},
          "response":{"message":"Refund successful","code":200}
        }}
        """, 200)

        req = ferbuy.Transaction.refund(
            transaction_id=10001,
            amount=100,
            currency='EUR'
        )

        self.assertEqual(req.request.command, 'EUR100')
        self.assertEqual(req.request.site_id, 1000)
        self.assertEqual(req.request.transaction_id, 10001)

        self.assertEqual(req.response.code, 200)
        self.assertEqual(req.response.message, "Refund successful")

    def test_invalid_refund(self):
        self.mock_response("""
        {"api":{
          "request":{"command":"EUR100","site_id":1000,"transaction_id":10001},
          "response":{"message":null,"code":400}
        }}
        """, 200)

        req = ferbuy.Transaction.refund(
            transaction_id=10001,
            amount=100,
            currency='EUR'
        )

        self.assertEqual(req.request.transaction_id, 10001)
        self.assertEqual(req.request.command, 'EUR100')
        self.assertEqual(req.request.site_id, 1000)

        self.assertEqual(req.response.code, 400)
        self.assertEqual(req.response.message, None)


class OrderResourceTests(ResourceTests):

    def test_valid_shippment(self):
        self.mock_response("""
        {"api":{
          "request":{"command":"DHL:123456","site_id":1000,"transaction_id":"10001abc"},
          "response":{"message":"Transaction 10001abc has been marked as shipped","code":200}
        }}
        """, 200)

        req = ferbuy.Order.shipped(
            transaction_id='10001abc',
            courier='DHL',
            tracking_number=123456
        )

        self.assertEqual(req.request.transaction_id, "10001abc")
        self.assertEqual(req.request.command, 'DHL:123456')
        self.assertEqual(req.request.site_id, 1000)

        self.assertEqual(req.response.code, 200)
        self.assertEqual(req.response.message,
                         "Transaction 10001abc has been marked as shipped")

    def test_invalid_shippment(self):
        self.mock_response("""
        {"api":{
          "request":{"command":"DHL:123456","site_id":1000,"transaction_id":10001},
          "response":{"message":"Transaction ID 10001 is already marked as shipped","code":400}
        }}
        """, 200)

        req = ferbuy.Order.shipped(
            transaction_id=10001,
            courier='DHL',
            tracking_number=123456
        )

        self.assertEqual(req.request.transaction_id, 10001)
        self.assertEqual(req.request.command, 'DHL:123456')
        self.assertEqual(req.request.site_id, 1000)

        self.assertEqual(req.response.code, 400)
        self.assertEqual(req.response.message,
                         "Transaction ID 10001 is already marked as shipped")

    def test_delivered_exception(self):
        with self.assertRaises(ValueError):
            ferbuy.Order.delivered(transaction_id=10001, date='invalid date')

    def test_valid_delivery(self):
        self.mock_response("""
        {"api":{
          "request": {"command":"2014-12-28 17:05:28","site_id":1000,"transaction_id":10001},
          "response": {"message":null,"code":200}
        }}
        """, 200)

        req = ferbuy.Order.delivered(
            transaction_id=10001,
            date=datetime.datetime(2014, 12, 28, 17, 05, 28)
        )

        self.assertEqual(req.request.transaction_id, 10001)
        self.assertEqual(req.request.command, '2014-12-28 17:05:28')
        self.assertEqual(req.request.site_id, 1000)

        self.assertEqual(req.response.code, 200)
        self.assertEqual(req.response.message, None)

    def test_invalid_delivery(self):
        self.mock_response("""
        {"api":{
          "request": {"command":"2014-12-28 17:05:28","site_id":1000,"transaction_id":10001},
          "response": {"message":null,"code":400}
        }}
        """, 200)

        req = ferbuy.Order.delivered(
            transaction_id=10001,
            date=datetime.datetime(2014, 12, 28, 17, 05, 28)
        )

        self.assertEqual(req.request.transaction_id, 10001)
        self.assertEqual(req.request.command, '2014-12-28 17:05:28')
        self.assertEqual(req.request.site_id, 1000)

        self.assertEqual(req.response.code, 400)
        self.assertEqual(req.response.message, None)


if __name__ == '__main__':
    unittest.main()
