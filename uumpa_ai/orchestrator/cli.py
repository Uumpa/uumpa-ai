import json
import click
from . import api, daemon
from ..catalog import api as catalog_api


@click.group()
def main():
    pass


@main.command()
def start_daemon():
    daemon.start()


@main.command()
@click.argument('content_json')
@click.option('--agent-id')
@click.option('--entrypoint-id')
def start_task(content_json, entrypoint_id, **kwargs):
    agent_user_id, task_number = api.start_task(
        content=json.loads(content_json),
        entrypoint_id=entrypoint_id or 'cli',
        **kwargs
    )
    click.echo(agent_user_id)


@main.command()
def start_watcher():
    api.start_watcher()


@main.command()
def init():
    api.init()
    click.echo("OK")


@main.command()
@click.argument('agent-user-id')
def update_agent(**kwargs):
    api.update_agent(**kwargs)
    click.echo("OK")


@main.command()
@click.argument('agent-deployment-id')
def update_agent_deployment(**kwargs):
    api.update_agent_deployment(**kwargs)
    click.echo("OK")


@main.command()
@click.argument('agent-id')
@click.argument('agent-user-id')
def deploy_agent(agent_id, agent_user_id):
    api.deploy_agent(catalog_api.get_item('agent', agent_id), agent_user_id)
    click.echo("OK")
