from openapi_genspec.helper import OpenAPIContext
from pprint import pprint
import yaml


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    o = OpenAPIContext("Discovery App", "master")
    o.path('/dataset')                                                      \
        .get()                                                              \
            .parameter('start', in_='query', required=False)                \
                .type('integer')                                            \
            .parameter('size', in_='query', required=False)                 \
                .type('integer', default=0, maximum=20)                     \
            .parameter('private', in_='query', required=True)               \
                .type('boolean')                                            \
    .path('/dataset/{id_}')                                                 \
        .parameter('id_', in_='path', required=True)                        \
            .type('string')                                                 \
               .description("Dataset Identifier")                           \
        .get()                                                              \
            .description('Get a dataset')                                   \
            .parameter('meta', in_='query', required=False)                 \
                .type('boolean', default=False)                             \
        .delete('del_dataset')
    yml = yaml.dump(o.document)
    print(yml)
