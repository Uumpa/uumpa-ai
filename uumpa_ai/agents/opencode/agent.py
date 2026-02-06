from ..base_agent import BaseAgent
from . import server


class OpenCodeAgent(BaseAgent):

    def get_deployment(self, agent_user_id):
        deployment = super().get_deployment(agent_user_id)
        deployment['spec']['template']['spec']['containers'].append({
            'name': 'opencode',
            'image': 'uumpa/opencode-agent-server:latest',
            'env': [
                {
                    'name': 'AGENT_USER_ID',
                    'value': agent_user_id
                }
            ],
            'ports': [
                {
                    'containerPort': 8080
                }
            ]
        })