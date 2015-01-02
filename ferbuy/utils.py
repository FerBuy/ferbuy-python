import logging

logger = logging.getLogger('ferbuy')

try:
    import json
except ImportError:
    json = None

if not (json and hasattr(json, 'loads')):
    try:
        import simplejson as json
    except ImportError:
        if not json:
            raise ImportError(
                "FerBuy required a JSON library, such as json or "
                "simplejson. Try to install the required library via "
                "'pip install json' or 'pip install simplejson'.")


class _Singleton(type):

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                _Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Singleton(_Singleton('SingletonMeta', (object,), {})):
    """Singleton pattern working with Python 2 & 3 versions"""
    pass
