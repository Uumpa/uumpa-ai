import functools


from . import forgejo
from .. import config


@functools.lru_cache(maxsize=None)
def all_labels():
    return {
        label['name']: label['id'] for label in
        forgejo.get_pagination_iterator(f'/repos/{config.FORGEJO_LOGBOOK_ORG_NAME}/logbook/labels')
    }


def label_id(label_name):
    return all_labels()[label_name]
