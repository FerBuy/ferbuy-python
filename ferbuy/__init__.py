# FerBuy Python binding

site_id = None
secret = None
env = 'live'

gateway_base = 'https://gateway.ferbuy.com'
api_base = 'https://gateway.ferbuy.com/api'

# Resources
from resources import Order, Transaction
from gateway import Gateway
