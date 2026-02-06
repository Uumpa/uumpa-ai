from .. import config
from ..logbook import api as logbook_api
from ..catalog import api as catalog_api


def get_next_task(agent_user_id=None):
    """Get the next open task this agent user should handle from the logbook
    Returns task number, task body dict, agent id and entrypoint id
    """
    if not agent_user_id:
        agent_user_id = config.AGENT_USER_ID
    return logbook_api.get_next_agent_task(agent_user_id)


def handle_next_task(agent_user_id=None):
    """Handle the next open task assigned to this agent user"""
    task_number, task_content, agent_id, entrypoint_id = get_next_task(agent_user_id)
    agent = catalog_api.get_item('agent', agent_id)
    entrypoint = catalog_api.get_item('entrypoint', entrypoint_id)
    agent.handle_task(task_number, task_content, entrypoint)


def get_agent_deployment_id(agent_user_id):
    """Convert agent user ID to agent deployment ID
    In most places we use agent user ID with underscores, but in Kubernetes we use deployment names with hyphens.
    """
    return agent_user_id.replace('_', '-')


def get_agent_user_id(agent_deployment_id):
    """Convert agent deployment ID to agent user ID"""
    return agent_deployment_id.replace('-', '_')
