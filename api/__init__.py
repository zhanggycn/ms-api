import os
from sanic.config import Config
from api.crud import crud_bp


__all__ =['crud_bp']

def load_config():
    conf  = Config()
    module = os.environ.get('SANIC_CONFIG_MODULE', None)
    if module:
        path = '%s.py' % module.replace('.', '/')
        conf.from_pyfile(path)
    else:
        import api.config
        conf.from_object(config)
    return conf

