import importlib
import os
import logging

from dotenv import load_dotenv
import pytest

from uumpa_ai import config
from uumpa_ai.logbook import forgejo, api as logbook_api
from uumpa_ai.orchestrator import api as orchestrator_api
from uumpa_ai.common import kubectl


class UumpaAiTestEnv:

    def __init__(self, logbook_org_name, kube_namespace):
        self.logbook_org_name = logbook_org_name
        self.kube_namespace = kube_namespace

    def setup(self):
        load_dotenv()
        os.environ['FORGEJO_LOGBOOK_ORG_NAME'] = self.logbook_org_name
        os.environ['KUBE_NAMESPACE'] = self.kube_namespace
        importlib.reload(config)

    def init(self):
        self.setup()
        logbook_api.init()
        orchestrator_api.init()

    def destroy_logbook(self):
        org = forgejo.get(f'/orgs/{self.logbook_org_name}')
        if org:
            for repo in forgejo.get_pagination_iterator(f'/orgs/{self.logbook_org_name}/repos'):
                forgejo.delete(f'/repos/{self.logbook_org_name}/{repo["name"]}')
            for team in forgejo.get_pagination_iterator(f'/orgs/{self.logbook_org_name}/teams'):
                forgejo.delete(f'/teams/{team["id"]}')
            forgejo.delete(f'/orgs/{self.logbook_org_name}')

    def destroy_orchestrator(self):
        kubectl.run('delete', 'namespace', self.kube_namespace, '--ignore-not-found=true', '--wait=false', check=True, with_namespace=False)

    def destroy(self):
        if os.getenv('DONT_DESTROY') != 'yes':
            self.destroy_logbook()
            self.destroy_orchestrator()


@pytest.fixture(scope='session')
def uumpa_ai_testenv_session():
    logging.basicConfig(level=logging.INFO)
    env = UumpaAiTestEnv('uumpa_ai_logbook_tests', 'uumpa-ai-tests')
    env.init()
    yield env
    env.destroy()


@pytest.fixture(autouse=True)
def uumpa_ai_testenv_function(uumpa_ai_testenv_session):
    uumpa_ai_testenv_session.setup()
    yield uumpa_ai_testenv_session
