import ferbuy

ferbuy.site_id = 1000
ferbuy.api_secret = 'you_api_secret'

result = ferbuy.Transaction.refund(
    transaction_id=10000,
    amount=100,
    currency='EUR'
)

if result.response.code == 200:
    print "Success:", result.response.message
else:
    print "Failure:", result.response.message
