import pytest
from openapi_genspec.helper import OpenAPIContext


def _basic_document():
    return {
        'openapi': '3.0.3',
        'info': {
            'title': '',
            'version': '',
        },
        'paths': {},
    }


def test_empty():
    o = OpenAPIContext('Title', 'Version')
    r = _basic_document()
    r['info']['title'] = 'Title'
    r['info']['version'] = 'Version'
    assert o.document == r


def test_description():
    o = OpenAPIContext('Title', 'Version', description='Something')
    r = _basic_document()
    r['info']['title'] = 'Title'
    r['info']['version'] = 'Version'
    r['info']['description'] = 'Something'
    assert o.document == r


def test_update_info():
    o = OpenAPIContext('Title', 'Version')
    o.info(
        title='NewTitle'
    ).info(
        version='NewVersion'
    ).info(
        termsOfService='http://example.com/'
    )
    r = _basic_document()
    r['info']['title'] = 'NewTitle'
    r['info']['version'] = 'NewVersion'
    r['info']['termsOfService'] = 'http://example.com/'
    assert o.document == r


def test_update_contact():
    o = OpenAPIContext('Title', 'Version')
    o.contact(name='SomeOne')
    r = _basic_document()
    r['info']['title'] = 'Title'
    r['info']['version'] = 'Version'
    r['info']['contact'] = {}
    r['info']['contact']['name'] = 'SomeOne'
    assert o.document == r


def test_update_license_name():
    o = OpenAPIContext('Title', 'Version')
    o.license(name='WTFPL')
    r = _basic_document()
    r['info']['title'] = 'Title'
    r['info']['version'] = 'Version'
    r['info']['license'] = {}
    r['info']['license']['name'] = 'WTFPL'
    assert o.document == r


def test_update_license_optional():
    o = OpenAPIContext('Title', 'Version')
    o.license(
        name='WTFPL',
        url='http://example.com/'
    )
    r = _basic_document()
    r['info']['title'] = 'Title'
    r['info']['version'] = 'Version'
    r['info']['license'] = {}
    r['info']['license']['name'] = 'WTFPL'
    r['info']['license']['url'] = 'http://example.com/'
    assert o.document == r


def test_add_path():
    o = OpenAPIContext('t', 'v')
    o.path('/api').get() \
        .parameter('p', in_='query', required=False) \
        .type('integer', default=0) \
        .end() \
        .path('/api2')

    r = {'openapi': '3.0.3',
         'info': {'title': 't', 'version': 'v'},
         'paths': {
             '/api': {
                 'get': {
                     'responses': {
                         '200': {'description': 'Success'}
                     },
                     'parameters': [
                         {
                             'name': 'p',
                             'in': 'query',
                             'required': False,
                             'schema': {
                                 'type': 'integer',
                                 'default': 0,
                             }
                         }
                     ]
                 }
             },
             '/api2': {},
         }
         }
    assert o.document == r


def test_summary():
    o = OpenAPIContext('t', 'v')
    o.path('/').summary('sum')
    r = {
        'info': {'title': 't', 'version': 'v'},
        'openapi': '3.0.3',
        'paths': {'/': {'summary': 'sum'}}
    }
    assert o.document == r


def test_desc():
    o = OpenAPIContext('t', 'v')
    o.path('/').description('d')
    r = {
        'info': {'title': 't', 'version': 'v'},
        'openapi': '3.0.3',
        'paths': {'/': {'description': 'd'}}
    }
    assert o.document == r


def test_multilevel_method_call():
    o = OpenAPIContext('t', 'v')
    with pytest.raises(AttributeError):
        o.path('/').get().info('cannot call')
