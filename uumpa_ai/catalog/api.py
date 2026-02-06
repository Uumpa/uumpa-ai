from copy import deepcopy
import importlib

from .. import config


def get_item(what, which):
    assert what in config.CATALOG, f'unknown catalog type: {what}'
    assert which in config.CATALOG[what], f'unknown catalog item for type {what}: {which}'
    conf = deepcopy(config.CATALOG[what][which])
    class_ = conf.pop('_class', None)
    assert class_, f'could not determine class for catalog item {which} of type {what}'
    *mods, class_name = class_.split('.')
    module = '.'.join(mods)
    mod = importlib.import_module(module)
    assert mod, f'could not import module {module} for catalog item {which} of type {what}'
    assert hasattr(mod, class_name), f'module {module} does not have class {class_name}'
    return getattr(mod, class_name)(which, conf)
