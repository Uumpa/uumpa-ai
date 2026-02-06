from ..catalog.base_catalog_item import BaseCatalogItem
from ..catalog import api as catalog_api


class SimpleRouter(BaseCatalogItem):

    def get_agent(self, agent_id=None, **kwargs):
        if not agent_id:
            agent_id = self.conf.get('default_agent')
        assert agent_id, 'could not determine agent ID'
        return catalog_api.get_item('agent', agent_id)
