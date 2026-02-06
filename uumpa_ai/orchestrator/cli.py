import json
import click
from . import api


@click.group()
def main():
    pass


@main.command()
@click.argument('content_json')
@click.option('--skip-deploy', is_flag=True)
@click.option('--agent-id')
@click.option('--entrypoint-id')
def start_task(content_json, entrypoint_id, **kwargs):
    click.echo(json.dumps(api.start_task(
        content=json.loads(content_json) if content_json else {},
        entrypoint_id=entrypoint_id or 'cli',
        **kwargs
    )))


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
