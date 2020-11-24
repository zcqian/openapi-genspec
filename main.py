from openapi_genspec.helper import OpenAPIDocument
from pprint import pprint
import yaml


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    o = OpenAPIDocument("Discovery App", "master")
    o.path('/dataset')                                          \
        .get()                                                  \
            .parameter('start', in_='query', required=False, type_='integer') \
            .parameter('size', in_='query', required=False, type_='integer',
                       default=0, maximum=20)                                 \
            .parameter('private', in_='query', required=True, type_='boolean')\
        .end()                                                                \
    .end()                                                                    \
    .path('/dataset/{id_}')                                                   \
        .parameter('id_', in_='path', required=True, type_='string',
                   description="Dataset Identifier")                        \
        .get()                                                              \
            .description('Get a dataset')                                   \
            .parameter('meta', in_='query', required=False, type_='boolean',
                       default=False)                                       \
        .end()                                                              \
        .delete()                                                           \
        .end()
    yml = yaml.dump(o.document)
    print(yml)

