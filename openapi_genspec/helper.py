from typing import List, Optional, MutableMapping, Type


class _BaseMetaClass(type):
    subclasses: MutableMapping[str, Type['_ChildContext']] = {}

    def __new__(cls, clsname, bases, attrs):
        def mk_ch_context_meth(child_context, field):
            def fn(self, **kwargs):
                ch_context = cls.subclasses[child_context](self)
                for at, v in kwargs.items():
                    if not at.startswith('_') and at in dir(ch_context):
                        meth = getattr(ch_context, at)
                        if callable(meth):
                            meth(v)
                            continue
                    raise AttributeError(f"Child does not have {at}")
                self.document[field] = ch_context.document
                if len(kwargs) > 0:
                    return self
                else:
                    return ch_context
            return fn

        def mk_attr_meth(field):
            def fn(self, v):
                self.document[field] = v
                return self
            return fn

        if 'CHILD_CONTEXTS' in attrs:
            for name, (ch_context, field) in attrs['CHILD_CONTEXTS'].items():
                docstring = f"""Set {field}
                            Create {ch_context} and set {field}
                            """
                meth = mk_ch_context_meth(ch_context, field)
                meth.__doc__ = docstring
                meth.__name__ = name
                attrs[name] = meth
        if 'ATTRIBUTE_FIELDS' in attrs:
            for name, field in attrs['ATTRIBUTE_FIELDS'].items():
                docstring = f"""Set {field} field"""
                meth = mk_attr_meth(field)
                meth.__doc__ = docstring
                meth.__name__ = name
                attrs[name] = meth

        new_cls = type.__new__(cls, clsname, bases, attrs)
        cls.subclasses[clsname] = new_cls
        return new_cls


class _BaseContext(metaclass=_BaseMetaClass):
    CHILD_CONTEXTS = {}
    ATTRIBUTE_FIELDS = {}

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
    ATTRIBUTE_FIELDS = {
        'summary': 'summary'
    }


class _HasDescription(_BaseContext):
    ATTRIBUTE_FIELDS = {
        'description': 'description'
    }


class _HasExternalDocs(_BaseContext):
    CHILD_CONTEXTS = {
        'external_docs': ('OpenAPIExternalDocsContext', 'externalDocs'),
    }


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
    CHILD_CONTEXTS = {}
    for http_method in ['get', 'put', 'post', 'delete', 'options', 'head',
                         'patch', 'trace']:
        CHILD_CONTEXTS[http_method] = ('OpenAPIOperation', http_method)


class OpenAPIOperation(_ChildContext, _HasSummary, _HasExternalDocs, _HasTags,
                       _HasDescription, _HasParameters):
    ATTRIBUTE_FIELDS = {
        'operation_id': 'operationId'
    }

    def __init__(self, parent):
        super(OpenAPIOperation, self).__init__(parent)
        self.document = {
            'responses': {
                '200': {
                    'description': "Success",
                }
            }
        }


class OpenAPIParameterContext(_ChildContext, _HasDescription):
    ATTRIBUTE_FIELDS = {
        'deprecated': 'deprecated',
        'allow_empty': 'allowEmptyValue',
        'style': 'style',
        'explode': 'explode',
        'allow_reserved': 'allowReserved',
        'schema': 'schema',
    }

    def __init__(self, parent, name: str, in_: str, required: bool):
        super(OpenAPIParameterContext, self).__init__(parent)
        self.document = {
            'name': name,
            'in': in_,
            'required': required,
        }

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
    ATTRIBUTE_FIELDS = {
        'url': 'url',
    }
