import json
import importlib

import click

from .. import config, common
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


for types_submodule in [
    'opencode'
]:
    main.add_command(getattr(importlib.import_module(f'.{types_submodule}.cli', __package__), 'main'), name=types_submodule.replace('_', '-'))
