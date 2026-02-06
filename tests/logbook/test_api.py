from uumpa_ai import config
from uumpa_ai.logbook import forgejo, api as logbook_api, agents
from uumpa_ai.catalog import api as catalog_api


def test():
    logbook_api.init()
    agent = catalog_api.get_item('agent', 'opencode')
    entrypoint = catalog_api.get_item('entrypoint', 'cli')
    content = {
        'request': 'Hello, World!'
    }
    logbook_api.create_agent_task(agent, entrypoint, content)
    agent_user_id, task_number = logbook_api.create_agent_task(agent, entrypoint, content)
    assert agent_user_id.startswith('agent_')
    issue = forgejo.get(f"/repos/{config.FORGEJO_LOGBOOK_ORG_NAME}/logbook/issues/{task_number}")
    assert issue['assignee']['login'] == agent_user_id
    assert [l['name'] for l in issue['labels']] == [agents.AGENT_TASK_LABEL]
    assert logbook_api.get_next_agent_task(agent_user_id) == (
        task_number,
        content,
        agent.id,
        entrypoint.id
    )
    _, new_task_number = logbook_api.create_agent_task(agent, entrypoint, content, agent_user_id)
    assert logbook_api.get_next_agent_task(agent_user_id) == (
        task_number,
        content,
        agent.id,
        entrypoint.id
    )
