import importlib
import logging

import click
from dotenv import load_dotenv

from .common.exceptions import UumpaAiEnvSetupException


load_dotenv()


@click.group()
def cli():
    logging.basicConfig(level=logging.INFO)


@click.command()
def init():
    from .orchestrator import api as orchestrator_api
    from .logbook import api as logbook_api
    logbook_api.init()
    orchestrator_api.init()


for submodule in [
    'logbook',
    'orchestrator',
    'agents',
]:
    mod = importlib.import_module(f'.{submodule}.cli', __package__)
    if mod and hasattr(mod, 'main'):
        cli.add_command(getattr(mod, 'main'), name=submodule.replace('_', '-'))


def main():
    try:
        cli()
    except UumpaAiEnvSetupException as e:
        click.echo(f'Error: {e}', err=True)
        exit(1)


if __name__ == "__main__":
    main()
