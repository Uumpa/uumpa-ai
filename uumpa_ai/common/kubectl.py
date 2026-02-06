import json
import subprocess
import os
import time

from .. import config


def get_env():
    env = os.environ.copy()
    if os.getenv("KUBECONFIG"):
        env["KUBECONFIG"] = os.environ["KUBECONFIG"]
    return env


def run(*args, with_namespace=True, **kwargs):
    return subprocess.run([
        "kubectl",
        *(["-n", config.KUBE_NAMESPACE] if with_namespace else []),
        *args
    ], env=get_env(), **kwargs)


def get(*args):
    p = subprocess.run([
        "kubectl", "get", "-n", config.KUBE_NAMESPACE, "-o", "json",
        *args
    ], capture_output=True, env=get_env())
    if p.returncode == 0:
        return json.loads(p.stdout.decode("utf-8"))
    else:
        return None


def apply(*objects):
    for obj in objects:
        subprocess.run([
            "kubectl", "apply", "-n", config.KUBE_NAMESPACE, "-f", "-"
        ], input=json.dumps(obj).encode("utf-8"), env=get_env(), check=True)


def patch_annotation(kind, name, annotation_key="uumpa.ai/refresh"):
    subprocess.run([
        "kubectl", "patch", kind, name, "-n", config.KUBE_NAMESPACE,
        "--type=merge",
        "-p",
        json.dumps({
            "metadata": {
                "annotations": {
                    annotation_key: str(int(time.time()))
                }
            }
        }).encode("utf-8")
    ], check=True, env=get_env())
