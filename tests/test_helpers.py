import pytest
from openapi_genspec.helper import OpenAPIDocument


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
    o = OpenAPIDocument('Title', 'Version')
    r = _basic_document()
    r['info']['title'] = 'Title'
    r['info']['version'] = 'Version'
    assert o.document == r


def test_description():
    o = OpenAPIDocument('Title', 'Version', description='Something')
    r = _basic_document()
    r['info']['title'] = 'Title'
    r['info']['version'] = 'Version'
    r['info']['description'] = 'Something'
    assert o.document == r


def test_update_info():
    o = OpenAPIDocument('Title', 'Version')
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
    o = OpenAPIDocument('Title', 'Version')
    o.contact(name='SomeOne')
    r = _basic_document()
    r['info']['title'] = 'Title'
    r['info']['version'] = 'Version'
    r['info']['contact'] = {}
    r['info']['contact']['name'] = 'SomeOne'
    assert o.document == r


def test_update_license_name():
    o = OpenAPIDocument('Title', 'Version')
    o.license(name='WTFPL')
    r = _basic_document()
    r['info']['title'] = 'Title'
    r['info']['version'] = 'Version'
    r['info']['license'] = {}
    r['info']['license']['name'] = 'WTFPL'
    assert o.document == r


def test_update_license_optional():
    o = OpenAPIDocument('Title', 'Version')
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
