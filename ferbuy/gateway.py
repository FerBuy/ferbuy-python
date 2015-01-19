import ferbuy
import hashlib


class Gateway(object):

    def __init__(self, post_data, site_id=None, secret=None, gateway_base=None):
        """Init Gateway

        Args:
            data (dict): Data which will be posted via form to FerBuy Gateway.
                Data should be valid and contain required fields accorind to
                FerBuy's technical documentation.
            site_id (int): Site ID assigned by FerBuy.
            secret (str): Shared secret for checksum verification.
            gateway_base (str): FerBuy's gateway url.
        """

        self.env = ferbuy.env

        if site_id:
            self.site_id = site_id
        else:
            self.site_id = ferbuy.site_id

        if secret:
            self.secret = secret
        else:
            self.secret = ferbuy.secret

        if gateway_base:
            self.gateway_base = gateway_base
        else:
            self.gateway_base = ferbuy.gateway_base

        if 'site_id' not in post_data:
            post_data['site_id'] = self.site_id

        if 'checksum' not in post_data:
            post_data['checksum'] = self.checksum(post_data)

        self.data = post_data

    def checksum(self, data):
        try:
            signature = "&".join([
                self.env,
                str(self.site_id),
                str(data['reference']),
                str(data['currency']),
                str(data['amount']),
                str(data['first_name']),
                str(data['last_name']),
                self.secret
            ])
            hash = hashlib.sha1(signature)
            return hash.hexdigest()
        except KeyError as e:
            raise KeyError("Missing required key {0}".format(e))

    @property
    def url(self):
        return "{0}/{1}/".format(self.gateway_base, self.env)

    @property
    def render(self):
        fields = ''
        for key, value in self.data.items():
            fields += '<input type="hidden" name="{0}" value="{1}">'.format(
                key, value)
        return fields

    @staticmethod
    def verify_callback(post_data):
        """Verify FerBuy's callback checksum.

        Args:
            post_data (dict): Dictionary containing values from POST request.

        Returns:
            boolean: True if checksum if correct, otherwise False.

        Raises:
            KeyError when required key is missing
        """
        try:
            signature = "&".join([
                ferbuy.env,
                str(post_data['reference']),
                str(post_data['transaction_id']),
                str(post_data['status']),
                str(post_data['currency']),
                str(post_data['amount']),
                ferbuy.secret
            ])

            hash = hashlib.sha1(signature)
            return post_data['checksum'] == hash.hexdigest()
        except KeyError as e:
            raise KeyError("Missing required key {0}".format(e))
