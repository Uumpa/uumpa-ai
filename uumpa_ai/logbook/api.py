import json
import logging

from . import forgejo, common, agents, init as init_module
from .. import config
# importing to expose for external use from the api module
from .agents import AGENT_TASK_STATUS_NEW, AGENT_TASK_STATUS_IN_PROGRESS, AGENT_TASK_STATUS_DONE


COMMENT_TYPE_AGENT_TASK_STATUS_UPDATE = 'agent_task_status_update'
COMMENT_TYPES = [
    v for k, v in globals().items() if k.startswith('COMMENT_TYPE_')
]

def init():
    """Initialize the Logbook org/repo in Forgejo"""
    if config.FORGEJO_LOCAL_DEVELOPMENT_INSTANCE:
        init_module.init_local_development_instance()
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


def get_agent_task_status(task_number):
    issue = forgejo.get(f'/repos/{config.FORGEJO_LOGBOOK_ORG_NAME}/logbook/issues/{task_number}')
    assert issue is not None, f'Failed to find the agent task issue {task_number}'
    if issue['state'] == 'closed':
        return AGENT_TASK_STATUS_DONE
    else:
        assert issue['state'] == 'open', f'Unexpected issue state: {issue["state"]}'
        status_labels = [label['name'] for label in issue['labels'] if label['name'].startswith(agents.AGENT_TASK_STATUS_LABEL_PREFIX)]
        if len(status_labels) > 1:
            raise Exception(f'Task {task_number} has multiple status labels: {status_labels}')
        elif len(status_labels) == 0:
            return agents.AGENT_TASK_STATUS_NEW
        else:
            return status_labels[0][len(agents.AGENT_TASK_STATUS_LABEL_PREFIX):]


def update_agent_task_status(task_number, status, verify_current_status=None):
    """Update the status of an agent task issue by changing its labels or closing the issue"""
    assert status in agents.AGENT_TASK_STATUSES, f'Invalid agent task status: {status}'
    current_status = get_agent_task_status(task_number)
    if verify_current_status:
        assert current_status == verify_current_status, f'Task {task_number} has unexpected current status {current_status}, expected {verify_current_status}'
    if current_status not in (agents.AGENT_TASK_STATUS_NEW, agents.AGENT_TASK_STATUS_DONE):
        forgejo.task_remove_labels(task_number, [agents.AGENT_TASK_STATUS_LABEL_PREFIX + current_status])
    if status == agents.AGENT_TASK_STATUS_DONE:
        forgejo.patch(f'/repos/{config.FORGEJO_LOGBOOK_ORG_NAME}/logbook/issues/{task_number}', json={'state': 'closed'})
    else:
        if current_status == agents.AGENT_TASK_STATUS_DONE:
            forgejo.patch(f'/repos/{config.FORGEJO_LOGBOOK_ORG_NAME}/logbook/issues/{task_number}', json={'state': 'open'})
        if status != agents.AGENT_TASK_STATUS_NEW:
            forgejo.task_add_labels(task_number, [agents.AGENT_TASK_STATUS_LABEL_PREFIX + status])


def add_agent_task_comment(task_number, comment_type, **data):
    assert comment_type in COMMENT_TYPES, f'Invalid comment type: {comment_type}'
    forgejo.post(f'/repos/{config.FORGEJO_LOGBOOK_ORG_NAME}/logbook/issues/{task_number}/comments', json={
        'body': json.dumps({"type": comment_type, **data}),
    })


def create_orchestrator_task(pid, hostname):
    """Create a new orchestrator task issue and return the task number"""
    assert get_orchestrator_task() is None, 'There is already an open orchestrator task, there can be only one'
    task = forgejo.post(f'/repos/{config.FORGEJO_LOGBOOK_ORG_NAME}/logbook/issues', json={
        'title': f'Orchestrator task on {hostname} (pid {pid})',
        'body': json.dumps({
            'pid': pid,
            'hostname': hostname,
        }),
        'labels': [common.label_id(common.ORCHESTRATOR_TASK_LABEL)],
    })
    task_number = task['number']
    logging.info(f'Created orchestrator task number {task_number}')
    return task_number


def get_orchestrator_task():
    orchestrator_tasks_iterator = forgejo.get_pagination_iterator(
        f'/repos/{config.FORGEJO_LOGBOOK_ORG_NAME}/logbook/issues',
        params={'state': 'open', 'type': 'issues', 'labels': common.ORCHESTRATOR_TASK_LABEL, 'sort': 'oldest'}
    )
    orchestrator_task = next(orchestrator_tasks_iterator, None)
    if orchestrator_task is None:
        return None
    else:
        assert next(orchestrator_tasks_iterator, None) is None, 'Multiple open orchestrator tasks found, there can be only one'
        return json.loads(orchestrator_task['body'])


def iterate_pending_agent_user_ids():
    """Iterate over all agent user IDs which have pending tasks assigned to them"""
    all_agent_user_ids = set()
    for task in forgejo.get_pagination_iterator(
        f'/repos/{config.FORGEJO_LOGBOOK_ORG_NAME}/logbook/issues',
        params={'state': 'open', 'type': 'issues', 'labels': agents.PENDING_AGENT_TASK_LABEL, 'sort': 'oldest'}
    ):
        for assignee in task['assignees']:
            username = assignee['username']
            if username.startswith(config.FORGEJO_AGENT_USER_PREFIX):
                if username not in all_agent_user_ids:
                    yield username
                all_agent_user_ids.add(username)
