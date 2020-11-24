from typing import List, Optional


class _Base:
    def __init__(self):
        self.document = {}

    def _set(self, k, v):
        self.document[k] = v


class _ChildItem(_Base):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def end(self):
        return self.parent


class _HasParameters(_Base):
    def parameter(self, name, in_, required,
                  type_: Optional[str] = None,
                  schema: Optional[dict] = None,
                  description: Optional[str] = None,
                  **kwargs):
        parameters = self.document.setdefault('parameters', [])
        parameter = {
            'name': name,
            'in': in_,
            'required': required
        }
        for k in ['description', 'required', 'deprecated', 'allowEmptyValue',
                  'style', 'explode', 'allowReserved']:
            v = kwargs.get(k, None)
            if v:
                parameter[k] = v
        if type_ and schema:  # shouldn't define both
            raise ValueError("schema and type both defined. Choose only one.")
        if type_:
            schema = {'type': type_}
            for k in ['minimum', 'maximum', 'default']:
                v = kwargs.get(k)
                if v:
                    schema[k] = v
        if schema:
            parameter['schema'] = schema
        if description:
            parameter['description'] = description
        parameters.append(parameter)
        return self


class _HasSummary(_Base):
    def summary(self, v):
        self._set('summary', v)
        return self


class _HasDescription(_Base):
    def description(self, v):
        self._set('description', v)
        return self


class _HasTags(_Base):
    def tag(self, t):
        tags = self.document.setdefault('tag', [])
        tags.append(t)
        return self


class OpenAPIDocument(_Base):
    def __init__(self, title: str, version: str,
                 description: Optional[str] = None):
        super(OpenAPIDocument, self).__init__()
        self.document = {
            'openapi': '3.0.3',
            'info': {
                'title': title,
                'version': version,
            },
            'paths': {},
        }
        if description:
            self.document['info']['description'] = description

    def _update_optional_fields(self, node: str, fields: List[str], kwargs):
        d = self.document
        for n in node.split('.'):
            d = d.setdefault(n, {})
        for k in fields:
            v = kwargs.get(k, None)
            if v:
                d[k] = v

    def info(self, **kwargs):
        """
        Set values in the 'info' field

        Set or update values in the 'info' field.

        :param str title: 'info.title'
        :param str description: 'info.description'
        :param str termsOfService: 'info.termsOfService'
        :param str version: 'info.version'

        """
        self._update_optional_fields(
            'info', ['title', 'description', 'termsOfService', 'version'],
            kwargs
        )
        return self

    def contact(self, **kwargs):
        """
        Set values in the 'info.contact' field

        :param str name: 'info.contact.name'
        :param str url: 'info.contact.url'
        :param str email: 'info.contact.email'
        """
        self._update_optional_fields(
            'info.contact', ['name', 'url', 'email'], kwargs)
        return self

    def license(self, name: str, **kwargs):
        """
        Set values in 'info.license'
        :param str name:
        :param str url:
        """
        self.document['info'].setdefault('license', {})['name'] = name
        self._update_optional_fields('info.license', ['url'], kwargs)
        return self

    def server(self):
        pass

    def path(self, path: str,
             summary: Optional[str] = None,
             description: Optional[str] = None):
        path_item = OpenAPIPathItem(self)
        if summary:
            path_item.summary(summary)
        if description:
            path_item.description(description)
        self.document['paths'][path] = path_item.document
        return path_item


class OpenAPIPathItem(_ChildItem, _HasSummary, _HasDescription,
                      _HasParameters):
    def _method_operation(self, method):
        operation = OpenAPIOperation(self, 'Success')
        self.document[method] = operation.document
        return operation

    def __getattr__(self, name):
        if name in ['get', 'put', 'post', 'delete', 'options', 'head',
                    'patch', 'trace']:
            def fn():
                return self._method_operation(name)
            return fn
        else:
            raise AttributeError(f'object has no attribute {name}')


class OpenAPIOperation(_ChildItem, _HasSummary,
                       _HasDescription, _HasParameters, _HasTags):
    def __init__(self, parent, success_desc):
        super(OpenAPIOperation, self).__init__(parent)
        self.document = {
            'responses': {
                '200': {
                    'description': success_desc,
                }
            }
        }
