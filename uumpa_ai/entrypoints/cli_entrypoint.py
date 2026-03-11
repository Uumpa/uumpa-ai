from ..catalog.base_catalog_item import BaseCatalogItem


class CliEntrypoint(BaseCatalogItem):

    def reply(self, message):
        print("--- CLI entrypoint reply ---")
        print(message)
        print("--- end of CLI entrypoint reply ---")
