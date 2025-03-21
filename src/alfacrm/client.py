import requests
from typing import Type, Dict
from pydantic import ValidationError
from exceptions import *
from models import *


class ALFACRM:
    """
    Основной клиент для работы с API ALFA CRM
    """

    def __init__(self, hostname: str, email: str, api_key: str):
        self.hostname = hostname
        self.email = email
        self.api_key = api_key
        self.token: Optional[str] = None
        self.branch_id: Optional[int] = None

        # Инициализация сущностей
        self._init_entities()

    class Entity:
        """
        Универсальный обработчик для сущностей API
        """

        def __init__(
                self,
                parent: 'ALFACRM',
                entity_name: str,
                filter_model: Type[ALFABaseModel] = None,
                create_model: Type[ALFABaseModel] = None,
                update_model: Type[ALFABaseModel] = None,
                branch_required: bool = False
        ):
            self.parent = parent
            self.entity_name = entity_name
            self.filter_model = filter_model
            self.create_model = create_model
            self.update_model = update_model
            self.branch_required = branch_required

        def _build_url(self, action: str, entity_id: Optional[int] = None) -> str:
            url_parts = []
            if self.branch_required:
                if not self.parent.branch_id:
                    raise ValueError("Branch ID is required for this entity")
                url_parts.append(str(self.parent.branch_id))

            url_parts.append(self.entity_name)

            if action != 'index':
                url_parts.append(action)

            url = f"https://{self.parent.hostname}/v2api/{'/'.join(url_parts)}"

            if entity_id:
                url += f"?id={entity_id}"

            return url

        def index(self, **params) -> Dict:
            try:
                if self.filter_model:
                    validated = self.filter_model(**params)
                    params = validated.model_dump(exclude_none=True)
            except ValidationError as e:
                raise ValidationError(f"Validation error: {e}") from e

            if 'page' not in params:
                return self._paginated_request(params)
            return self.parent._request('POST', self._build_url('index'), data=params)

        def create(self, **data) -> Dict:
            try:
                if self.create_model:
                    validated = self.create_model(**data)
                    data = validated.model_dump(exclude_none=True)
            except ValidationError as e:
                raise ValidationError(f"Validation error: {e}") from e

            return self.parent._request('POST', self._build_url('create'), data=data)

        def update(self, entity_id: int, **data) -> Dict:
            try:
                if self.update_model:  # Валидация для update
                    validated = self.update_model(**data)
                    data = validated.model_dump(exclude_none=True)
            except ValidationError as e:
                raise ValidationError(f"Update validation error: {e}") from e

            return self.parent._request('POST', self._build_url('update', entity_id), data=data)


        def _paginated_request(self, params: Dict) -> Dict:
            all_items = []
            page = 0
            while True:
                params['page'] = page
                response = self.parent._request('POST', self._build_url('index'), data=params)
                if not (items := response.get('items')):
                    break
                all_items.extend(items)
                page += 1
            return {'items': all_items, 'total': len(all_items)}

    def _init_entities(self):
        """Инициализация всех поддерживаемых сущностей"""

        self.customer = self.Entity(
            self,
            'customer',
            filter_model=CustomerFilter,
            create_model=CustomerCreate,
            update_model=CustomerUpdate,
            branch_required=True
        )

        self.branch = self.Entity(
            self,
            'branch',
            filter_model=BranchBase,
            create_model=BranchCreate,
            update_model=BranchUpdate,
            branch_required=False
        )
        self.CGI = self.Entity(
            self,
            'CGI',
            filter_model=CGICreate,
            create_model=CGIUpdate,
            update_model=CGICustomerFilter,
            branch_required=False
        )


        # Добавьте другие сущности по аналогии:
        # self.branch = self.Entity(...)
        # self.lesson = self.Entity(...)

    def _request(self, method: str, url: str, data: Dict = None) -> Dict:
        headers = {
            'X-ALFACRM-TOKEN': self.token,
            'Content-Type': 'application/json'
        }

        try:
            response = requests.request(
                method=method,
                url=url,
                json=data,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            self._handle_http_error(e, response)
        except requests.RequestException as e:
            raise APIRequestError(f"Request failed: {str(e)}") from e

    def _handle_http_error(self, error: requests.HTTPError, response: requests.Response):
        status_code = response.status_code
        try:
            error_data = response.json()
        except ValueError:
            error_data = {}

        message = error_data.get('message', 'Unknown error')

        if status_code == 401:
            raise AuthenticationError("Invalid credentials") from error
        elif status_code == 404:
            raise NotFoundError(message) from error
        elif status_code == 429:
            raise RateLimitExceeded(message) from error
        else:
            raise APIRequestError(
                f"API request failed ({status_code}): {message}",
                response_data=error_data
            ) from error

    def authenticate(self):
        """Выполнить аутентификацию и получить токен"""
        url = f"https://{self.hostname}/v2api/auth/login"
        try:
            response = requests.post(url, json={
                "email": self.email,
                "api_key": self.api_key
            })
            response.raise_for_status()
            self.token = response.json().get('token')
            if not self.token:
                raise AuthenticationError("No token received")
        except requests.HTTPError as e:
            raise AuthenticationError(f"Authentication failed: {e.response.text}") from e