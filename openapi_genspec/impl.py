import re


class _BaseOpenAPIObject:
    REQUIRED_FIELDS = {}
    OPTIONAL_FIELDS = {}
    PATTERN_FIELDS = {}
    EXTENSIONS = False  # Most will set this to True

    _validation_types = {
        'string': str,
        'integer': int,
        'number': float,
    }
    _validation_expr = [
        (r'^([A-Za-z_][A-Za-z0-9_]+)$', 'simple'),
        (r'^\[(.+)]$', 'list'),
        (r'^Map\[(.+),(.+)]$', 'map'),
        (r'^(.+?)\|(.+)$', 'or'),  # hacky, but as of now this should work fine
    ]

    def __init__(self):
        super(_BaseOpenAPIObject, self).__init__()
        self.fields = {}
        for field_name in self.REQUIRED_FIELDS:
            self.fields[field_name] = None

        cls_name = self.__class__.__name__
        if not cls_name.startswith('_'):
            if cls_name in self._validation_types:
                if self._validation_types[cls_name] == self.__class__:
                    pass
                else:
                    raise Exception("Two object class with same name")
            else:
                self._validation_types[cls_name] = self.__class__

    def __getitem__(self, key):
        return self.fields[key]

    def __setitem__(self, key, value):
        # will call validation before to_dict()
        self.fields[key] = value

    def validate(self):
        for req_field in self.REQUIRED_FIELDS:
            v = self.fields.get(req_field, None)
            if v is None:
                raise KeyError(
                    f"Required field {req_field} does not exist"
                )
        all_fixed_fields = self.REQUIRED_FIELDS.copy()
        all_fixed_fields.update(self.OPTIONAL_FIELDS)
        for k, v in self.fields.items():
            bad_field_e = ValueError(f"field {k} is not allowed in {self}")
            if k in all_fixed_fields:
                oas_type = all_fixed_fields[k]
                if self._parse_and_validate_item(oas_type, v):
                    pass
                else:
                    raise ValueError(
                        f"Invalid value for {k} in {self}, " +
                        f"expected a {oas_type} but got {v}"
                    )
                continue
            elif self.EXTENSIONS and k.startswith("x-"):
                continue
            # make sure this branch takes place LAST because it raises
            elif len(self.PATTERN_FIELDS) > 0:
                for regex, oas_type in self.PATTERN_FIELDS.items():
                    m = re.match(regex, k)
                    if m is None:
                        continue
                    if self._parse_and_validate_item(oas_type, v):
                        break
                    else:
                        raise ValueError(
                            f"Invalid value for {k} in {self}, " +
                            f"expected a {oas_type} but got {v}"
                        )
                else:
                    raise bad_field_e
            else:
                raise bad_field_e
        return True

    def _parse_and_validate_item(self, oas_type, value):
        oas_type = re.sub(r'\s+', '', oas_type)
        expr = []
        for regex, t in self._validation_expr:
            expr.append((re.compile(regex), t))
        for regex, t in expr:
            m = regex.match(oas_type)
            if m is None:
                continue
            else:
                if t == 'simple':
                    return self._validate_simple(m.groups()[0], value)
                elif t == 'list':
                    return self._validate_list(m.groups()[0], value)
                elif t == 'map':
                    kt, vt = m.groups()
                    return self._validate_map(kt, vt, value)
                elif t == 'or':
                    t, ot = m.groups()
                    return self._validate_or(t, ot, value)
                else:
                    raise ValueError(f"No val. handler for {t}")
        else:
            raise ValueError(f"Cannot process type definition: {oas_type}")

    def _validate_simple(self, oas_type, value):
        t = self._validation_types[oas_type]
        if isinstance(value, t):  # ignore linter warnings here
            return True
        else:
            return False

    def _validate_list(self, oas_type, value):
        if not isinstance(value, list):
            return False
        for v in value:
            if self._parse_and_validate_item(oas_type, v):
                pass
            else:
                return False
        return True

    def _validate_map(self, k_type, v_type, value):
        if not isinstance(value, dict):
            return False
        for k, v in value.items():
            if self._parse_and_validate_item(k_type, k) and \
                    self._parse_and_validate_item(v_type, v):
                pass
            else:
                return False
        return True

    def _validate_or(self, one_type, other_types, value):
        return self._parse_and_validate_item(one_type, value) or \
               self._parse_and_validate_item(other_types, value)

    def to_dict(self) -> dict:
        self.validate()
        # because it has been validated, no additional checks needed
        d = {}
        for k, v in self.fields.items():
            d[k] = self._dict_helper(v)
        return d

    def _dict_helper(self, item):
        if isinstance(item, _BaseOpenAPIObject):
            return item.to_dict()
        elif isinstance(item, list):
            return [self._dict_helper(i) for i in item]
        elif isinstance(item, dict):
            return {k: self._dict_helper(v) for k, v in item.items()}
        else:
            return item


class OpenAPI(_BaseOpenAPIObject):
    REQUIRED_FIELDS = {
        'openapi': 'string',
        'info': 'Info',
        'paths': 'Paths'
    }
    OPTIONAL_FIELDS = {
        'servers': '[Server]',
        'components': 'Components',
        'security': '[SecurityRequirement]',
        'tags': '[Tag]',
        'externalDocs': 'ExternalDocumentation',
    }
    EXTENSIONS = True

    def __init__(self):
        super(OpenAPI, self).__init__()
        self.fields['openapi'] = '3.0.3'


class Info(_BaseOpenAPIObject):
    REQUIRED_FIELDS = {
        'title': 'string',
        'version': 'string',
    }
    OPTIONAL_FIELDS = {
        'description': 'string',
        'termsOfService': 'string',
        'contact': 'Contact',
        'license': 'License'
    }
    EXTENSIONS = True


class Contact(_BaseOpenAPIObject):
    OPTIONAL_FIELDS = {
        'name': 'string',
        'url': 'string',
        'email': 'string',
    }
    EXTENSIONS = True


class License(_BaseOpenAPIObject):
    REQUIRED_FIELDS = {
        'name': 'string',
    }
    OPTIONAL_FIELDS = {
        'url': 'string',
    }
    EXTENSIONS = True


class Server(_BaseOpenAPIObject):
    REQUIRED_FIELDS = {
        'url': 'string',
    }
    OPTIONAL_FIELDS = {
        'description': 'string',
        'variables': 'Map[string, ServerVariable]',
    }
    EXTENSIONS = True


class ServerVariable(_BaseOpenAPIObject):
    REQUIRED_FIELDS = {
        'default': 'string',
    }
    OPTIONAL_FIELDS = {
        'enum': '[string]',
        'description': 'string',
    }
    EXTENSIONS = True

    def validate(self):
        super(ServerVariable, self).validate()
        if self['enum'] is not None and len(self['enum']) > 0:
            pass
        else:
            raise ValueError("enum SHOULD NOT be empty")


class Components(_BaseOpenAPIObject):
    OPTIONAL_FIELDS = {
        'schemas': 'Map[string, Schema|Reference]',
        'responses': 'Map[string, Response|Reference]',
        'parameters': 'Map[string, Parameter|Reference]'
    }
    # FIXME: implement
    EXTENSIONS = True


class Paths(_BaseOpenAPIObject):
    PATTERN_FIELDS = {
        r'^/.*': 'PathItem',
    }
    EXTENSIONS = True


class PathItem(_BaseOpenAPIObject):
    OPTIONAL_FIELDS = {
        '$ref': 'string',
        'summary': 'string',
        'description': 'string',
        'get': 'Operation',
        'put': 'Operation',
        'post': 'Operation',
        'delete': 'Operation',
        'options': 'Operation',
        'head': 'Operation',
        'patch': 'Operation',
        'trace': 'Operation',
        'servers': '[Server]',
        'parameters': '[Parameter|Reference]',
    }
    EXTENSIONS = True


class Schema(_BaseOpenAPIObject):
    pass  # FIXME: implement
