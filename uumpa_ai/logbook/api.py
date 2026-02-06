import json
import logging

from . import forgejo, common, agents, init as init_module
from .. import config


def init():
    """Initialize the Logbook org/repo in Forgejo"""
    init_module.init_org()
    init_module.init_repo()


def create_agent_task(agent, entrypoint, content, agent_user_id=None):
    """Create a new agent task issue and assign it to an agent user
    returns the assigned agent_user_id and the task number
    """
    task = forgejo.post(f'/repos/{config.FORGEJO_LOGBOOK_ORG_NAME}/logbook/issues', json={
        'title': f'Agent task',
        'body': json.dumps({
            'agent_id': agent.id,
            'entrypoint_id': entrypoint.id,
            'content': content,
        }),
        'labels': [common.label_id(agents.PENDING_AGENT_TASK_LABEL)],
    })
    task_number = task['number']
    logging.info(f'Created pending agent task number {task_number}')
    # the following is to ensure a single created issue is handled at a time to prevent conflicts
    # it doesn't matter now but in the future we might want to support more complex task assignment logic
    while True:
        issue = next(forgejo.get_pagination_iterator(
            f'/repos/{config.FORGEJO_LOGBOOK_ORG_NAME}/logbook/issues',
            params={'state': 'open', 'type': 'issues', 'labels': agents.PENDING_AGENT_TASK_LABEL, 'sort': 'oldest'}
        ), None)
        assert issue is not None, 'Failed to find the created agent task'
        if issue['number'] == task_number:
            break
    if not agent_user_id:
        agent_user_id = agents.create_agent_user()
    forgejo.patch(f'/repos/{config.FORGEJO_LOGBOOK_ORG_NAME}/logbook/issues/{task_number}', json={
        'assignees': [agent_user_id],
    })
    forgejo.put(f'/repos/{config.FORGEJO_LOGBOOK_ORG_NAME}/logbook/issues/{task_number}/labels', json={
        'labels': [agents.AGENT_TASK_LABEL],
    })
    return agent_user_id, task_number


def get_next_agent_task(agent_user_id):
    """Get the next open agent task issue assigned to the given agent user
    returns: task number, task content dict, agent id, entrypoint ID, or Nones if no task found
    """
    issue = next(forgejo.get_pagination_iterator(
        f'/repos/{config.FORGEJO_LOGBOOK_ORG_NAME}/logbook/issues',
        params={'state': 'open', 'type': 'issues', 'labels': agents.AGENT_TASK_LABEL, 'sort': 'oldest', 'assigned_by': agent_user_id}
    ), None)
    if issue:
        body = json.loads(issue['body'])
        return issue['number'], body['content'], body['agent_id'], body['entrypoint_id']
    else:
        return None, None, None, None
