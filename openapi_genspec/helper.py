from typing import List, Optional


class _BaseContext:
    def __init__(self):
        self.document = {}

    def _set(self, k, v):
        self.document[k] = v


class _ChildContext(_BaseContext):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def end(self):
        """Explicitly return to the parent context

        Returns:
            Parent context
        """
        return self.parent

    def __getattr__(self, attr_name: str):
        multilevel_allow = ['path', 'get', 'put', 'post', 'delete', 'options',
                            'head', 'patch', 'trace']
        if not attr_name.startswith('_'):
            if attr_name in dir(self.parent) or (
                    attr_name in multilevel_allow and
                    hasattr(self.parent, attr_name)):
                return getattr(self.parent, attr_name)
        raise AttributeError()


class _HasParameters(_BaseContext):
    def parameter(self, name, in_, required):
        parameters = self.document.setdefault('parameters', [])
        param_context = OpenAPIParameterContext(self, name, in_, required)
        parameters.append(param_context.document)
        return param_context


class _HasSummary(_BaseContext):
    def summary(self, v):
        self._set('summary', v)
        return self


class _HasDescription(_BaseContext):
    def description(self, v):
        self._set('description', v)
        return self


class _HasExternalDocs(_BaseContext):
    def external_docs(self, url):
        ext_doc_context = OpenAPIExternalDocsContext(self, url)
        self.document['externalDocs'] = ext_doc_context.document
        return ext_doc_context


class _HasTags(_BaseContext):
    def tag(self, t):
        tags = self.document.setdefault('tag', [])
        tags.append(t)
        return self


class OpenAPIContext(_HasExternalDocs):
    def __init__(self, title: str, version: str,
                 description: Optional[str] = None):
        super(OpenAPIContext, self).__init__()
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

    def server(self, url: str, description: Optional[str] = None):
        servers = self.document.setdefault('servers', [])
        server = {
            'url': url
        }
        if description:
            server['description'] = description
        servers.append(server)
        return self

    def path(self, path: str,
             summary: Optional[str] = None,
             description: Optional[str] = None):
        path_item = OpenAPIPathContext(self)
        if summary:
            path_item.summary(summary)
        if description:
            path_item.description(description)
        self.document['paths'][path] = path_item.document
        return path_item


class OpenAPIPathContext(_ChildContext, _HasSummary, _HasDescription,
                         _HasParameters):
    # def __init__(self, parent):
    #     super(OpenAPIPathItem, self).__init__(parent)
    #     for method in ['get', 'put', 'post', 'delete', 'options', 'head',
    #                  'patch', 'trace']:
    #         # def fn():
    #         #     return self._method_operation(method)
    #         self.__setattr__(method, lambda: self._method_operation(method))

    def _method_operation(self, method, operation_id: Optional[str] = None):
        operation_context = OpenAPIOperation(self)
        self.document[method] = operation_context.document
        if operation_id:
            operation_context.operation_id(operation_id)
        return operation_context

    def __getattr__(self, attr_name):
        if attr_name in ['get', 'put', 'post', 'delete', 'options', 'head',
                         'patch', 'trace']:
            def fn(op_id=None):
                return self._method_operation(attr_name, op_id)

            return fn
        else:
            return super(OpenAPIPathContext, self).__getattr__(attr_name)


class OpenAPIOperation(_ChildContext, _HasSummary, _HasExternalDocs, _HasTags,
                       _HasDescription, _HasParameters):
    def __init__(self, parent):
        super(OpenAPIOperation, self).__init__(parent)
        self.document = {
            'responses': {
                '200': {
                    'description': "Success",
                }
            }
        }

    def operation_id(self, op_id):
        self.document['operationId'] = op_id
        return self


class OpenAPIParameterContext(_ChildContext, _HasDescription):
    def __init__(self, parent, name: str, in_: str, required: bool):
        super(OpenAPIParameterContext, self).__init__(parent)
        self.document = {
            'name': name,
            'in': in_,
            'required': required,
        }

    def deprecated(self, dep: bool):
        self._set('deprecated', dep)
        return self

    def allow_empty(self, ae: bool):
        self._set('allowEmptyValue', ae)
        return self

    def style(self, sty: str):
        self._set('style', sty)
        return self

    def explode(self, exp: bool):
        self._set('explode', exp)
        return self

    def allow_reserved(self, ar: bool):
        self._set('allowReserved', ar)
        return self

    def schema(self, sch: dict):
        self._set('schema', sch)
        return self

    def type(self, typ: str, **kwargs):
        schema = {
            'type': typ,
        }
        for k in ['minimum', 'maximum', 'default']:
            v = kwargs.get(k)
            if v is not None:
                schema[k] = v
        self.schema(schema)
        return self


class OpenAPIExternalDocsContext(_ChildContext, _HasDescription):
    def __init__(self, parent, url):
        super(OpenAPIExternalDocsContext, self).__init__(parent)
        self.document = {
            'url': url,
        }
