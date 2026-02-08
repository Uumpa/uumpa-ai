import signal
import logging

from ..logbook import api as logbook_api
from . import watcher, init as init_module
from ..common import kubectl
from .. import config
from ..catalog import api as catalog_api
from ..agents import api as agents_api


def deploy_agent(agent, agent_user_id):
    kubectl.apply(agent.get_deployment(agent_user_id))


def start_task(content, skip_deploy=False, agent_id=None, entrypoint_id=None):
    entrypoint = catalog_api.get_item('entrypoint', entrypoint_id)
    router = catalog_api.get_item('router', config.ORCHESTRATOR_DEFAULT_ROUTER)
    agent = router.get_agent(content=content, agent_id=agent_id, entrypoint=entrypoint)
    agent_user_id, task_number = logbook_api.create_agent_task(agent, entrypoint, content)
    if not skip_deploy:
        deploy_agent(agent, agent_user_id)
    return agent_user_id, task_number


def start_watcher():
    state = {
        'terminate': False,
        'running': False,
    }

    def handle_terminate(signum, frame):
        if state['running']:
            logging.info('Received termination signal, waiting for current update to finish...')
            state['terminate'] = True
        else:
            logging.info('Received termination signal, exiting...')
            exit(0)

    signal.signal(signal.SIGTERM, handle_terminate)
    signal.signal(signal.SIGINT, handle_terminate)
    for event in watcher.events_iterator("apps/v1", "Deployment", config.KUBE_NAMESPACE):
        if event['type'] == 'MODIFIED':
            state['running'] = True
            update_agent(agents_api.get_agent_user_id(event['object'].metadata.name))
            state['running'] = False
            if state['terminate']:
                logging.info('Terminating...')
                exit(0)


def update_agent_deployment(agent_deployment_id):
    kubectl.patch_annotation('deployment', agent_deployment_id)


def update_agent(agent_user_id):
    print(f'Updating agent: {agent_user_id}')


def init():
    init_module.init()
