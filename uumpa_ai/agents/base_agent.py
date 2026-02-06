from ..catalog.base_catalog_item import BaseCatalogItem
from .api import get_agent_deployment_id


class BaseAgent(BaseCatalogItem):

    def handle_task(self, task_number, task_content, entrypoint):
        raise NotImplementedError()

    def get_deployment(self, agent_user_id):
        agent_deployment_id = get_agent_deployment_id(agent_user_id)
        return {
            'apiVersion': 'apps/v1',
            'kind': 'Deployment',
            'metadata': {
                'name': agent_deployment_id,
                'labels': {
                    'app': agent_deployment_id
                }
            },
            'spec': {
                'replicas': 1,
                'selector': {
                    'matchLabels': {
                        'app': agent_deployment_id
                    }
                },
                'template': {
                    'metadata': {
                        'labels': {
                            'app': agent_deployment_id
                        }
                    },
                    'spec': {
                        'containers': [
                            {
                                'name': 'agent',
                                'image': 'uumpa/agent:latest',
                                'env': [
                                    {
                                        'name': 'AGENT_USER_ID',
                                        'value': agent_user_id
                                    }
                                ]
                            }
                        ]
                    }
                }
            }
        }
