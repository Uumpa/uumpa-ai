import logging
import signal
import os
import subprocess

from ..logbook import api as logbook_api


def initialize(state):
    assert 'pid' not in state
    state['pid'] = os.getpid()
    state['hostname'] = os.uname().nodename
    state['orchestrator_task_number'] = logbook_api.create_orchestrator_task(state['pid'], state['hostname'])
    state['agents'] = {}
    update(state)


def update(state):
    logging.info('Updating...')
    for agent_user_id in logbook_api.iterate_pending_agent_user_ids():
        if agent_user_id not in state['agents']:
            state['agents'][agent_user_id] = {
                'process': subprocess.Popen(['uai', 'agents', 'handle_tasks', agent_user_id]),
            }



def start():
    state = {
        'terminate': False,
        'updating': False,
    }

    def handle_terminate(*args):
        if state['updating']:
            logging.info('Received termination signal, waiting for current update to finish...')
            state['terminate'] = True
        else:
            logging.info('Received termination signal, no update in progress, exiting...')
            exit(0)

    def handle_update(*args):
        state['updating'] = True
        try:
            update(state)
        finally:
            state['updating'] = False
            if state['terminate']:
                logging.info('Terminating...')
                exit(0)

    signal.signal(signal.SIGTERM, handle_terminate)
    signal.signal(signal.SIGINT, handle_terminate)
    signal.signal(signal.SIGHUP, handle_update)
    initialize(state)
    logging.info('Initialization complete, waiting for SIGHUP to update')
    while True:
        signal.pause()
