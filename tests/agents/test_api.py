from uumpa_ai.agents import api as agents_api
from uumpa_ai.logbook import api as logbook_api
from uumpa_ai.catalog import api as catalog_api
from uumpa_ai.entrypoints.cli_entrypoint import CliEntrypoint
from uumpa_ai.agents.opencode import OpenCodeAgent


def test(monkeypatch):
    mock_open_code_handle_task_calls = []

    class MockOpenCodeAgent(OpenCodeAgent):
        def handle_task(self, tn, tc, e):
            mock_open_code_handle_task_calls.append((tn, tc, e.id))

    def mock_get_item(what, which):
        if what == 'agent':
            return MockOpenCodeAgent(which, {})
        elif what == 'entrypoint':
            return CliEntrypoint(which, {})
        else:
            return None

    monkeypatch.setattr('uumpa_ai.catalog.api.get_item', mock_get_item)
    agent = catalog_api.get_item('agent', 'opencode')
    entrypoint = catalog_api.get_item('entrypoint', 'cli')
    agent_user_id, task_number = logbook_api.create_agent_task(agent, entrypoint, {'request': 'Hello, World!'})
    assert agents_api.get_next_task(agent_user_id) == (
        task_number,
        {'request': 'Hello, World!'},
        'opencode',
        'cli',
    )
    agents_api.handle_next_task(agent_user_id)
    assert mock_open_code_handle_task_calls == [(task_number, {'request': 'Hello, World!'}, 'cli')]
    assert agents_api.get_agent_deployment_id('agent_123') == 'agent-123'
    assert agents_api.get_agent_user_id('agent-123') == 'agent_123'
