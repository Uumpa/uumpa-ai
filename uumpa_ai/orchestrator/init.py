from ..common import kubectl
from .. import config


def init_kubernetes():
    kubectl.get('ns', config.KUBE_NAMESPACE) or kubectl.apply({
        "apiVersion": "v1",
        "kind": "Namespace",
        "metadata": {
            "name": config.KUBE_NAMESPACE
        }
    })


def init():
    init_kubernetes()
