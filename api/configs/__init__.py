import os

from sanic.config import Config


def load_config():
    conf  = Config()
    module = os.environ.get('SANIC_CONFIG_MODULE', None)
    if module:
        path = '%s.py' % module.replace('.', '/')
        conf.from_pyfile(path)
    else:
        import configs.config
        conf.from_object(configs.config)
    return conf

