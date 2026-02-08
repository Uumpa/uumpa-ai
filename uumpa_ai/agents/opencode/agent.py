import os
from contextlib import contextmanager
import subprocess
import signal
import time

import requests

from ..base_agent import BaseAgent
from ... import config


class OpenCodeAgent(BaseAgent):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.opencode_process = None
        signal.signal(signal.SIGINT, self.opencode_terminate)
        signal.signal(signal.SIGTERM, self.opencode_terminate)

    def opencode_terminate(self, *args, **kwargs):
        if self.opencode_process:
            print('Terminating opencode server...')
            self.opencode_process.terminate()
            self.opencode_process.wait()
            self.opencode_process = None
            print('Opencode server terminated')

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

    # these methods are called from inside the agent container

    def handle_task(self, task_number, task_content, entrypoint):
        print(f'Handling task {task_number} with content {task_content} and entrypoint {entrypoint}')
        print(config.AGENT_USER_ID)
        self.opencode_terminate()
        print('Starting opencode server...')
        self.opencode_process = subprocess.Popen(
            ['opencode', 'serve', '--port', '4096', '--hostname', '127.0.0.1'],
            cwd=os.path.expanduser("~/workspace"),
        )
        try:
            while True:
                try:
                    assert requests.get('http://127.0.0.1:4096/global/health').json()['healthy']
                    break
                except:
                    time.sleep(0.1)
            opencode_version = requests.get('http://127.0.0.1:4096/global/health').json()['version']
            print(f'Opencode v{opencode_version} is ready')
            session = requests.post('http://127.0.0.1:4096/session', json={}).json()

        finally:
            self.opencode_terminate()
