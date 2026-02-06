import urllib3

from kubernetes import config as kubernetes_config
from kubernetes.client import api_client
from kubernetes.client.exceptions import ApiException
from kubernetes.dynamic.client import DynamicClient

from .. import config


def events_iterator(api_version, kind, namespace):
    if config.KUBE_INCLUSTER_CONFIG:
        kubernetes_config.load_incluster_config()
    else:
        kubernetes_config.load_kube_config()
    client = DynamicClient(api_client.ApiClient())
    api = client.resources.get(api_version=api_version, kind=kind)
    resource_version = None
    while True:
        try:
            for event in api.watch(namespace=namespace, resource_version=resource_version, allow_watch_bookmarks=True):
                resource_version = event['object'].metadata.resourceVersion
                if event['type'] != 'BOOKMARK':
                    yield event
        except ApiException as err:
            if err.status == 410:
                resource_version = None
            else:
                raise
        except urllib3.exceptions.ProtocolError:
            pass
