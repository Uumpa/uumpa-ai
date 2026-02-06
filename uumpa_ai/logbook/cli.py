import json

import click

from . import api
from ..catalog import api as catalog_api


@click.group()
def main():
    pass


@main.command()
def init():
    api.init()
    click.echo("OK")


@main.command()
@click.argument("agent_id")
@click.argument("entrypoint_id")
@click.argument("body_json")
def create_agent_task(agent_id, entrypoint_id, body_json):
    click.echo(json.dumps(create_agent_task(
        catalog_api.get_item('agent', agent_id),
        catalog_api.get_item('entrypoint', entrypoint_id),
        json.loads(body_json)
    )))
