from datetime import date
import requests
from typing import Optional, Dict, Type
from .models import CustomerFilter, BranchFilter  # Импорт всех моделей


class ALFACRM:
    def __init__(self, hostname: str, email: str, api_key: str):
        self.hostname = hostname
        self.email = email
        self.api_key = api_key
        self.token = self._auth()
        self.branch_id: Optional[int] = None

    class Entity:
        def __init__(self, parent, entity_name: str,
                     filter_model: Optional[Type] = None,
                     branch_required: bool = False):
            self.parent = parent
            self.entity_name = entity_name
            self.filter_model = filter_model
            self.branch_required = branch_required

        def index(self, **params) -> Dict:
            if self.filter_model:
                validated = self.filter_model(**params)
                params = validated.model_dump(exclude_none=True)

            # Реализация запроса...

        # Другие методы...

    def __init_entities(self):
        self.customer = self.Entity(
            self, 'customer',
            filter_model=CustomerFilter,
            branch_required=True
        )
        # Инициализация других сущностей...

    def _auth(self) -> str:
        url = f"https://{self.hostname}/v2api/auth/login"
        response = requests.post(url, json={
            "email": self.email,
            "api_key": self.api_key
        })
        response.raise_for_status()
        return response.json()['token']