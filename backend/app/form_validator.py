from functools import cached_property

from google.cloud.datastore import Client
from google.oauth2.service_account import Credentials


class FormValidator:
    def __init__(self, service_account_file: str):
        self._service_account_file = service_account_file

    @cached_property
    def datastore_client(self) -> Client:
        credentials = Credentials.from_service_account_file(self._service_account_file)
        return Client(credentials=credentials, project=credentials.project_id)

    def validate(self, form_id: int) -> bool:
        key = self.datastore_client.key("Survey", form_id)
        entity = self.datastore_client.get(key)
        return True if entity else False
