import unittest
import pkgutil


def test_modules():
    for _, modname, _ in pkgutil.iter_modules(__path__):
        if modname.startwith('test_'):
            yield 'ferbuy.test.{0}'.format(modname)

def all():
    return unittest.defaultTestLoader.loadTestsFromNames(test_modules())
