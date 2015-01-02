# FerBuy Python bindings

The FerBuy library provides integration access to the FerBuy Gateway.

## Dependencies

* Python 2.6, 2.7, 3,3 or 3.4.
* [json](https://docs.python.org/2/library/json.html)
* [requests](http://docs.python-requests.org/en/latest/) *(optional)*

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

Example API call to refund a transaction for 1 EUR:

```python
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
```

Example call for marking order as shipped:

```python
    import ferbuy

    ferbuy.site_id = 1000
    ferbuy.api_secret = 'you_api_secret'

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
