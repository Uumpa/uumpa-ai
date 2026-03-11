import os
from contextlib import contextmanager
import subprocess
import signal
import time
import secrets
import logging

from ..base_agent import BaseAgent
from . import opencode
from ...logbook import api as logbook_api


class OpenCodeAgent(BaseAgent):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.opencode_process = None
        signal.signal(signal.SIGINT, self.opencode_terminate)
        signal.signal(signal.SIGTERM, self.opencode_terminate)

    def opencode_terminate(self, *args, **kwargs):
        if self.opencode_process:
            logging.info('Terminating opencode server...')
            self.opencode_process.terminate()
            self.opencode_process.wait()
            self.opencode_process = None
            logging.info('Opencode server terminated')

    # these methods are called from the orchestrator

    def get_deployment(self, agent_user_id):
        deployment = super().get_deployment(agent_user_id)
        deployment['spec']['template']['spec']['volumes'] = [
            {
                'name': 'home',
                'persistentVolumeClaim': {
                    'claimName': 'home',
                }
            }
        ]
        volume_mounts = [
            {
                'name': 'home',
                'mountPath': '/home/ubuntu',
            }
        ]
        deployment['spec']['template']['spec']['containers'][0]['volumeMounts'] = volume_mounts
        return deployment

    # this method is for local development, to help emulate the environment inside the agent container
    @contextmanager
    def setup_for_local_development(self, agent_user_id):
        with super().setup_for_local_development(agent_user_id):
            yield

    def handle_task(self, agent_user_id, task_number, task_content, entrypoint):
        logbook_api.update_agent_task_status(task_number, logbook_api.AGENT_TASK_STATUS_IN_PROGRESS, verify_current_status=logbook_api.AGENT_TASK_STATUS_NEW)
        prompt = task_content['prompt']
        opencode.OPENCODE_PASSWORD = secrets.token_urlsafe(12)
        logging.info(f'Starting opencode server with password: {opencode.OPENCODE_PASSWORD}')
        self.opencode_terminate()
        self.opencode_process = subprocess.Popen(
            ['opencode', 'serve', '--port', '-1', '--hostname', '127.0.0.1'],
            cwd=os.path.expanduser("~/workspace"),
            stdout=subprocess.PIPE,
            env={**os.environ, 'OPENCODE_SERVER_PASSWORD': opencode.OPENCODE_PASSWORD}
        )
        for line in self.opencode_process.stdout:
            line = line.decode().strip()
            logging.info(line)
            if line.startswith('opencode server listening on http://127.0.0.1:'):
                opencode.OPENCODE_PORT = int(line.split(':')[-1])
                break
        try:
            opencode_version = None
            while opencode_version is None:
                try:
                    res = opencode.global_health()
                    assert res['healthy']
                    opencode_version = res.get('version') or 'unknown'
                except:
                    time.sleep(0.1)
            logging.info(f'Opencode version {opencode_version} is ready')
            session_id = opencode.start_session()
            logging.info(f'Session ID: {session_id}')
            reply = opencode.text_prompt_sync(session_id, prompt)
            logbook_api.add_agent_task_comment(
                task_number, logbook_api.COMMENT_TYPE_AGENT_TASK_STATUS_UPDATE,
                reply=reply
            )
            entrypoint.reply(reply)
        finally:
            self.opencode_terminate()
            logbook_api.update_agent_task_status(task_number, logbook_api.AGENT_TASK_STATUS_DONE, verify_current_status=logbook_api.AGENT_TASK_STATUS_IN_PROGRESS)
