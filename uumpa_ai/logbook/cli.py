import json

import click

from . import api, agents
from ..catalog import api as catalog_api
from . import forgejo as forgejo_api


@click.group()
def main():
    pass


@main.command()
def init():
    api.init()
    click.echo("OK")


@main.command()
def create_agent_user():
    click.echo(agents.create_agent_user())


@main.command()
@click.argument("agent_id")
@click.argument("entrypoint_id")
@click.argument("body_json")
@click.option('--agent-user-id')
def create_agent_task(agent_id, entrypoint_id, body_json, agent_user_id):
    res_agent_user_id, task_number = api.create_agent_task(
        catalog_api.get_item('agent', agent_id),
        catalog_api.get_item('entrypoint', entrypoint_id),
        json.loads(body_json),
        agent_user_id=agent_user_id,
    )
    if agent_user_id:
        click.echo(f'Using provided agent user ID: {agent_user_id}', err=True)
    else:
        click.echo(f'Created agent user ID: {res_agent_user_id}', err=True)
    click.echo(task_number)



@main.command()
@click.argument('command')
@click.argument('args_json')
@click.argument('kwargs_json')
def forgejo(command, args_json, kwargs_json):
    click.echo(json.dumps(getattr(forgejo_api, command)(*json.loads(args_json), **json.loads(kwargs_json))))


@main.command()
@click.argument('task_number')
@click.argument('status')
@click.option('--verify-current-status')
def update_agent_task_status(**kwargs):
    api.update_agent_task_status(**kwargs)
    click.echo("OK")


@main.command()
@click.argument('task_number')
def get_agent_task_status(task_number):
    click.echo(api.get_agent_task_status(task_number))


@main.command()
@click.argument('task_number')
@click.argument('comment_type')
@click.argument('data_json')
def add_agent_task_comment(task_number, comment_type, data_json):
    api.add_agent_task_comment(task_number, comment_type, **json.loads(data_json))
    click.echo("OK")


@main.command()
@click.option('--task-number')
def get_orchestrator_task(**kwargs):
    click.echo(json.dumps(api.get_orchestrator_task(**kwargs)))
