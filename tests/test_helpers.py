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
    o = OpenAPIContext()
    o.info(title='Title', version='Version')
    r = _basic_document()
    r['info']['title'] = 'Title'
    r['info']['version'] = 'Version'
    assert o.document == r


def test_description():
    o = OpenAPIContext()
    o.info()\
        .title('Title')\
        .version('Version')\
        .description('Something')
    r = _basic_document()
    r['info']['title'] = 'Title'
    r['info']['version'] = 'Version'
    r['info']['description'] = 'Something'
    assert o.document == r


def test_add_server():
    o = OpenAPIContext()
    o.info(title='t', version='v')
    o.server('http://localhost/')
    r = {
        'info': {'title': 't', 'version': 'v'},
        'openapi': '3.0.3',
        'paths': {},
        'servers': [{'url': 'http://localhost/'}]
    }
    assert o.document == r


def test_add_path():
    o = OpenAPIContext()
    o.info(title='t', version='v')
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
    o = OpenAPIContext()
    o.info(title='t', version='v')
    o.path('/').summary('sum')
    r = {
        'info': {'title': 't', 'version': 'v'},
        'openapi': '3.0.3',
        'paths': {'/': {'summary': 'sum'}}
    }
    assert o.document == r


def test_desc():
    o = OpenAPIContext()
    o.info(title='t', version='v')
    o.path('/').description('d')
    r = {
        'info': {'title': 't', 'version': 'v'},
        'openapi': '3.0.3',
        'paths': {'/': {'description': 'd'}}
    }
    assert o.document == r


def test_multilevel_method_call():
    o = OpenAPIContext()
    o.info(title='t', version='v')
    with pytest.raises(AttributeError):
        o.path('/').get().info('cannot call')
