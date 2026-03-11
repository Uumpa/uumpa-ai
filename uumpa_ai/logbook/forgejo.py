import requests

from .. import config
from ..common.exceptions import UumpaAiEnvSetupException


def request(method, path, **kwargs):
    if not config.FORGEJO_API_URL and not config.FORGEJO_ORCHESTRATOR_ADMIN_API_TOKEN:
        raise UumpaAiEnvSetupException('Log book is not configured, see uumpa_ai/logbook/README.md for setup instructions')
    url = f'{config.FORGEJO_API_URL}/v1/{path}'
    return requests.request(
        method,
        url,
        headers={
            'Authorization': f'Bearer {config.FORGEJO_ORCHESTRATOR_ADMIN_API_TOKEN}',
            'Content-Type': 'application/json',
        },
        **kwargs
    )


def get(path, **kwargs):
    res = request("GET", path, **kwargs)
    if res.status_code == 404:
        return None
    elif res.status_code == 200:
        return res.json()
    else:
        raise Exception(f'Forgejo get {path} failed: {res.status_code} {res.text}')


def post(path, method="POST", **kwargs):
    res = request(method, path, **kwargs)
    if res.status_code < 200 or res.status_code >= 300:
        raise Exception(f'Forgejo {method} {path} failed: {res.status_code} {res.text}')
    return res.json() if res.content else None


def patch(path, **kwargs):
    return post(path, method="PATCH", **kwargs)


def put(path, **kwargs):
    return post(path, method="PUT", **kwargs)


def delete(path, **kwargs):
    return post(path, method="DELETE", **kwargs)


def get_pagination_iterator(path, **kwargs):
    page = 1
    per_page = 50
    while True:
        params = kwargs.pop('params', {})
        params.update({'page': page, 'limit': per_page})
        res = get(path, params=params, **kwargs)
        if not res or len(res) == 0:
            break
        for item in res:
            yield item
        if len(res) < per_page:
            break
        page += 1


def task_get_labels(task_number):
    labels = get(f'/repos/{config.FORGEJO_LOGBOOK_ORG_NAME}/logbook/issues/{task_number}/labels')
    return [label['name'] for label in labels] if labels else []


def task_add_labels(task_number, labels):
    return post(f'/repos/{config.FORGEJO_LOGBOOK_ORG_NAME}/logbook/issues/{task_number}/labels', json={
        'labels': labels,
    })


def task_remove_labels(task_number, labels):
    return [
        delete(f'/repos/{config.FORGEJO_LOGBOOK_ORG_NAME}/logbook/issues/{task_number}/labels/{label}')
        for label in labels
    ]
