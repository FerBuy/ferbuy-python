import datetime

from ferbuy.api_requestor import APIRequestor


class Resource(object):
    # only JSON format is supported with the API binding
    output = 'json'


class Order(Resource):

    @staticmethod
    def shipped(transaction_id, courier, tracking_number):
        """Mark order as shipped and return a response object.

        Mark order as shipped as soon as you have shipped it. Marking an order
        as shipped, will send an invoice to the consumer and will release
        the transaction amount for payment to you as merchant.

        Args:
            transaction_id (int): Transaction ID with FerBuy.
            courier (str): Name of the courier company delivering the order.
                Supported couriers are: DHL, EMS, Fedex, POSTCZ, POSTPL, UPS.
                It's possible to define your own eg. 'DPD'.
            tracking_number (int|str): Tracking number supported by courier
                company.

        Returns:
            FerbuyObject: Response object containing API's request and response.
        """
        requestor = APIRequestor()

        post_data = {
            'command': '{0}:{1}'.format(courier, tracking_number),
            'output_type': Resource.output,
            'site_id': requestor.site_id,
            'transaction_id': transaction_id,
        }
        post_data['checksum'] = requestor.sign(**post_data)

        response = requestor.request('post', '/MarkOrderShipped', post_data)
        return response

    @staticmethod
    def delivered(transaction_id, date):
        """Mark order as being delivered and return a response object.

        For some merchants the `ConfirmDeliver` function is required. If this
        function is optional, we do recommend that you use this function anyway.

        Args:
            transaction_id (int): Transaction ID with FerBuy.
            date (datetime): Datetime object representing date of delivery.

        Returns:
            FerbuyObject: Response object containing API's request and response.

        Raises:
            ValueError: If `date` is not an instance of datetime object.
        """
        if not isinstance(date, datetime.datetime):
            raise ValueError("expecting `date` to be datetime object")

        requestor = APIRequestor()

        post_data = {
            'command': date.strftime("%Y-%m-%d %H:%I:%S"),
            'output_type': Resource.output,
            'site_id': requestor.site_id,
            'transaction_id': transaction_id,
        }
        post_data['checksum'] = requestor.sign(**post_data)

        response = requestor.request('post', '/ConfirmDelivery', post_data)
        return response


class Transaction(Resource):

    @staticmethod
    def refund(transaction_id, amount, currency):
        """Refund a transaction and return a response object.

        Sometimes orders are being returned. In case that happens,
        you can do a refund. This can be a full refund or a partial refund.

        Args:
            transaction_id (int): Transaction ID with FerBuy.
            amount (int): Refunded amount without decimal point.
                For example to refund 20.98 EUR the amount needs to be `2098`.
            currency: Currency code following ISO 4217 format.
                Supported currencies are: USD, EUR, CZK, PLN, SGD.

        Returns:
            FerbuyObject: Response object containing API's request and response.
        """
        requestor = APIRequestor()

        post_data = {
            'command': '{0}{1}'.format(currency, amount),
            'output_type': Resource.output,
            'site_id': requestor.site_id,
            'transaction_id': transaction_id,
        }
        post_data['checksum'] = requestor.sign(**post_data)

        response = requestor.request('post', '/RefundTransaction', post_data)
        return response
