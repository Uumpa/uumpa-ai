import click

from ...catalog import api as catalog_api


@click.group()
def main():
    pass


@main.command()
@click.option('--agent-id')
def start_server(agent_id):
    if not agent_id:
        agent_id = 'opencode'
    catalog_api.get_item('agent', agent_id).start_server()
