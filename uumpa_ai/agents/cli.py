import json
import importlib

import click

from . import api
from ..catalog import api as catalog_api


@click.group()
def main():
    pass


@main.command()
@click.argument('agent_user_id')
def get_next_task(agent_user_id):
    click.echo(json.dumps(api.get_next_task(agent_user_id)))


@main.command()
@click.argument('agent_user_id')
def handle_next_task(agent_user_id):
    api.handle_next_task(agent_user_id)
    click.echo("OK")


@main.command()
@click.argument('agent_id')
@click.argument('agent_user_id')
@click.argument('task_number')
@click.argument('task_content_json')
@click.argument('entrypoint_id')
def handle_task(agent_id, agent_user_id, task_number, task_content_json, entrypoint_id):
    task_content = json.loads(task_content_json)
    agent = catalog_api.get_item('agent', agent_id)
    entrypoint = catalog_api.get_item('entrypoint', entrypoint_id)
    with agent.setup_for_local_development(agent_user_id):
        agent.handle_task(task_number, task_content, entrypoint)


for types_submodule in [
    'opencode'
]:
    main.add_command(getattr(importlib.import_module(f'.{types_submodule}.cli', __package__), 'main'), name=types_submodule.replace('_', '-'))
