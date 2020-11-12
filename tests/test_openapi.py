import pytest

from openapi_genspec import *
from openapi_genspec.impl import _BaseOpenAPIObject


def _basic_obj():
    o = OpenAPI()
    o['info'] = Info()
    o['info']['title'] = 'Title'
    o['info']['version'] = '0.0.1'
    o['paths'] = Paths()
    return o

def test_openapi_init():
    o = OpenAPI()
    assert o is not None


def test_openapi_missing_fields():
    o = OpenAPI()
    with pytest.raises(KeyError):
        o.to_dict()


def test_openapi_basic():
    o = _basic_obj()
    o.to_dict()
    assert o is not None


def test_bad_type():
    o = _basic_obj()
    o['servers'] = Server()
    with pytest.raises(ValueError):
        o.to_dict()


def test_openapi_list():
    o = _basic_obj()
    o['servers'] = [Server()]
    o['servers'][0]['url'] = 'http://localhost/'
    o.to_dict()


def test_openapi_extended_true():
    o = _basic_obj()
    o['x-extended-info'] = 'x-'
    o.to_dict()


def test_openapi_extended_false():
    o = _BaseOpenAPIObject()
    o['x-extended-info'] = 'x-'
    with pytest.raises(ValueError):
        o.validate()
