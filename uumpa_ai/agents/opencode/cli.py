import json

import click

from . import opencode


@click.group()
def main():
    pass


@main.command()
def iterate_events():
    for event in opencode.iterate_events():
        click.echo(json.dumps(event))


@main.command()
def start_session():
    session_id = opencode.start_session()
    click.echo(session_id)


@main.command()
@click.argument('session_id')
@click.argument('prompt')
def text_prompt(session_id, prompt):
    click.echo(opencode.text_prompt_sync(session_id, prompt))
