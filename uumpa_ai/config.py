import os
import yaml



# example: https://forgejo.example.com/api
FORGEJO_API_URL = os.getenv("FORGEJO_API_URL", "").rstrip("/")
# admin token for the orchestrator, it should have full admin permissions on the forgejo instance
FROGEJO_ORCHESTRATOR_ADMIN_API_TOKEN = os.getenv("FROGEJO_ORCHESTRATOR_ADMIN_API_TOKEN")
FORGEJO_LOGBOOK_ORG_NAME = os.getenv("FORGEJO_LOGBOOK_ORG_NAME", "uumpa_ai_logbook")
FORGEJO_AGENT_USER_PREFIX = os.getenv("FORGEJO_AGENT_USER_PREFIX", "agent")
FORGEJO_AGENT_USER_EMAIL_TEMPLATE = os.getenv("FORGEJO_AGENT_USER_EMAIL_TEMPLATE", "agent+{basename}@localhost")

# if set to "yes", the kubernetes client will use in-cluster config, otherwise it will use kubeconfig file
KUBE_INCLUSTER_CONFIG = os.getenv("KUBE_INCLUSTER_CONFIG", "").lower() == "yes"
KUBE_NAMESPACE = os.getenv("KUBE_NAMESPACE", "uumpa-ai")
# this is used inside agent deployments to identify themselves
AGENT_USER_ID = os.getenv("AGENT_USER_ID")
ORCHESTRATOR_DEFAULT_ROUTER = os.getenv("ORCHESTRATOR_DEFAULT_ROUTER", "default")

CATALOG_FILE_PATH = os.getenv("CATALOG_FILE_PATH")
if not CATALOG_FILE_PATH:
    CATALOG_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'catalog.yaml')
CATALOG = {}
if CATALOG_FILE_PATH:
    with open(CATALOG_FILE_PATH) as f:
        CATALOG.update(**yaml.safe_load(f))
