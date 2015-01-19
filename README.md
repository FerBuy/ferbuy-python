# FerBuy Python bindings

The FerBuy library provides integration access to the FerBuy Gateway.

## Dependencies

* Python 2.6, 2.7, 3,3 or 3.4.
* [json](https://docs.python.org/2/library/json.html)
* *(optional)* [requests](http://docs.python-requests.org/en/latest/)

## Installation

You need to checkout the source code from GitHub to install the package.
The easiest way to do so it to run:

```
$ git clone https://github.com/FerBuy/ferbuy-python.git
$ cd ferbuy-python
$ pip setup.py install
```

See http://www.pip-installer.org/en/latest/index.html for instructions
on installing pip. If you are on a system with easy_install but not
pip, you can use easy_install instead. If you're not using virtualenv,
you may have to prefix those commands with `sudo`. You can learn more
about virtualenv at http://www.virtualenv.org/

## Testing

We commit to being compatible with Python 2.6+, Python 3.1+ and PyPy.
To run all test suites it is assumed that the package is in your PYTHONPATH, if
not add `ferbuy` package to your PYTHONPATH:
```
$ cd ferbuy-python
$ export PYTHONPATH=$PYTHONPATH:$PWD
```

To run all tests execute:
```
$ cd ferbuy
$ python -m unittest discover
```

## Quick Start Example

### Example Gateway usage

In the Gateway example we are using [Flask](http://flask.pocoo.org/)
microframework to demonstrate customer redirect and callback handling.

Here is the simple redirect example:
```python
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
```

This is how the template looks like:
```html
<form method="post" action="{{ gateway.url }}">
    {{ gateway.render|safe }}
    <input type="submit" value="Submit">
</form>
```

To verify the call we need to extend the app above and add the following code:
```python
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
```

The full working example can be found in
[example](example/gateway_example.py) folder.

### Example API usage

Example API call to refund a transaction for 1 EUR:

```python
import ferbuy

ferbuy.site_id = 1000
ferbuy.secret = 'your_secret'

result = ferbuy.Transaction.refund(
    transaction_id=10000,
    amount=100,
    currency='EUR'
)

if result.response.code == 200:
    print "Success:", result.response.message
else:
    print "Failure:", result.response.message
```

Example call for marking order as shipped:

```python
import ferbuy

ferbuy.site_id = 1000
ferbuy.secret = 'your_secret'

result = ferbuy.Order.shipped(
    transaction_id=10000,
    courier='DHL',
    tracking_number=12345
)

if result.response.code == 200:
    print "Success:", result.response.message
else:
    print "Failure:", result.response.message
```

## Documentation

TO BE ADDED.

## License

See the LICENSE file.
