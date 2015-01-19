import ferbuy
import random

from flask import Flask
from flask import request
from flask import render_template

app = Flask(__name__)

ferbuy.site_id = 1000
ferbuy.secret = 'your_secret'
ferbuy.env = 'demo'

@app.route('/')
def redirect():
    data = {
        'reference': 'Transaction{0}'.format(random.randint(10000, 99999)),
        'currency': 'EUR',
        'amount': random.randint(10000, 29999),
        'return_url_ok': 'http://www.your-site.com/success/',
        'return_url_cancel': 'http://www.your-site.com/failed/',
        'first_name': 'John',
        'last_name': 'Doe',
        'address': 'Business Center',
        'postal_code': 'SLM000',
        'city': 'Landville',
        'country_iso': 'US',
        'email': 'demo@email.com',
    }
    gateway = ferbuy.Gateway(data)
    return render_template('redirect.html', gateway=gateway)

@app.route('/callback', methods=['POST', 'PUT'])
def callback():
    if ferbuy.Gateway.verify_callback(request.form):
        status = int(request.form['status'])
        if status == 200:
            # Transaction successful
            pass
        elif status >= 400:
            # Transaction failed
            pass
    else:
        # Unable to verify callback
        pass
    return "{0}.{1}".format(request.form['transaction_id'],
                            request.form['status'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
