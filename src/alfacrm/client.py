# client.py
import requests
from typing import Type, Dict, Optional, Any
from pydantic import ValidationError
from datetime import datetime, timedelta
from .exceptions import *
from .models import *


class ALFACRM:
    """Основной клиент для работы с API ALFA CRM"""

    def __init__(self, hostname: str, email: str, api_key: str):
        self.hostname = hostname
        self.email = email
        self.api_key = api_key
        self.token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
        self.branch_id: Optional[int] = None

        self._init_entities()

    class Entity:
        """Универсальный обработчик для сущностей API"""

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

        def _build_url(self, action: str, **params) -> str:
            """Формирование URL с учетом особенностей API ALFA CRM"""
            parts = []

            if self.branch_required:
                if not self.parent.branch_id:
                    raise MissingBranchError("Branch ID is required for this entity")
                parts.append(str(self.parent.branch_id))

            parts.append(self.entity_name)

            if action != 'index':
                parts.append(action)

            url = f"https://{self.parent.hostname}/v2api/{'/'.join(parts)}"

            query = '&'.join([f"{k}={v}" for k, v in params.items() if v is not None])
            if query:
                url += f"?{query}"

            return url

        def index(self, **params) -> Dict:
            """Получение списка сущностей с фильтрацией"""
            try:
                validated_params = self.filter_model(**params).model_dump(
                    exclude_none=True) if self.filter_model else {}
            except ValidationError as e:
                raise RequestValidationError(e.errors()) from e

            if 'page' not in validated_params:
                return self._paginated_request(validated_params)
            return self.parent._request('POST', self._build_url('index'), data=validated_params)

        def create(self, **data) -> Dict:
            """Создание новой сущности"""
            try:
                validated = self.create_model(**data).model_dump(exclude_none=True) if self.create_model else data
            except ValidationError as e:
                raise RequestValidationError(e.errors()) from e

            return self.parent._request('POST', self._build_url('create'), data=validated)

        def update(self, entity_id: int, **data) -> Dict:
            """Обновление существующей сущности"""
            try:
                validated = self.update_model(**data).model_dump(exclude_none=True) if self.update_model else data
            except ValidationError as e:
                raise RequestValidationError(e.errors()) from e

            return self.parent._request('POST', self._build_url('update', id=entity_id), data=validated)

        def delete(self, entity_id: int, **params) -> Dict:
            """Удаление сущности"""
            return self.parent._request('POST', self._build_url('delete', **params, id=entity_id))

        def _paginated_request(self, params: Dict) -> Dict:
            """Автоматическая обработка пагинации"""
            all_items = []
            page = 0
            total = 0

            while True:
                params['page'] = page
                response = self.parent._request('POST', self._build_url('index'), data=params)
                items = response.get('items', [])
                all_items.extend(items)

                if total == 0:
                    total = response.get('total', 0)

                if not items or len(all_items) >= total:
                    break

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

        self.customer_groups = self.Entity(
            self,
            'cgi/customer',
            filter_model=CGICustomerFilter,
            create_model=CGICreate,
            update_model=CGIUpdate,
            branch_required=True
        )

        self.group_customers = self.Entity(
            self,
            'cgi',
            filter_model=CGIGroupFilter,
            create_model=CGICreate,
            update_model=CGIUpdate,
            branch_required=True
        )

        self.communication = self.Entity(
            self,
            'communication',
            filter_model=CommunicationFilter,
            create_model=CommunicationCreate,
            update_model=CustomerUpdate,
            branch_required=True
        )

        self.customer_tariff = self.Entity(
            self,
            'customer_tariff',
            filter_model=CustomerTariffFilter,
            update_model=CustomerTariffUpdate,
            create_model=CustomerTariffCreate,
            branch_required=True
        )

        self.group = self.Entity(
            self,
            'group',
            filter_model=GroupFilter,
            update_model=GroupBase,
            create_model=GroupCreate,
            branch_required = True
        )

        self.lead_reject = self.Entity(
            self,
            'lead_reject',
            filter_model=LeadRejectFilter,
            update_model=LeadRejectUpdate,
            create_model=LeadRejectCreate,
            branch_required = True
        )

        # Location - Локации
        self.location = self.Entity(
            self,
            'location',
            filter_model=LocationFilter,
            create_model=LocationCreate,
            update_model=LocationUpdate,
            branch_required=True
        )

        # Room - Аудитории
        self.room = self.Entity(
            self,
            'room',
            filter_model=RoomFilter,
            create_model=RoomCreate,
            update_model=RoomUpdate,
            branch_required=True
        )

        # Subject - Предметы обучения
        self.subject = self.Entity(
            self,
            'subject',
            filter_model=SubjectFilter,
            create_model=SubjectCreate,
            update_model=SubjectUpdate,
            branch_required=True
        )

        # StudyStatus - Статусы обучения
        self.study_status = self.Entity(
            self,
            'study-status',
            filter_model=StudyStatusFilter,
            create_model=StudyStatusCreate,
            update_model=StudyStatusUpdate,
            branch_required=True
        )

        # LeadStatus - Этапы воронки
        self.lead_status = self.Entity(
            self,
            'lead-status',
            filter_model=LeadStatusFilter,
            create_model=LeadStatusCreate,
            update_model=LeadStatusUpdate,
            branch_required=True
        )

        # LeadSource - Источники лидов
        self.lead_source = self.Entity(
            self,
            'lead-source',
            filter_model=LeadSourceFilter,
            create_model=LeadSourceCreate,
            update_model=LeadSourceUpdate,
            branch_required=True
        )

        # Pay - Платежи
        self.pay = self.Entity(
            self,
            'pay',
            filter_model=PayFilter,
            create_model=PayCreate,
            update_model=PayUpdate,
            branch_required=True
        )

        # Lesson - Уроки
        self.lesson = self.Entity(
            self,
            'lesson',
            filter_model=LessonFilter,
            create_model=LessonCreate,
            update_model=LessonUpdate,
            branch_required=True
        )

        # Bonus - Бонусы
        self.bonus = self.Entity(
            self,
            'bonus',
            filter_model=BonusHistoryFilter,
            create_model=BonusChangeRequest,  # Для bonus-add/bonus-spend
            branch_required=True
        )


        # Log - История изменений
        self.log = self.Entity(
            self,
            'log',
            filter_model=LogFilter,
            branch_required=True
        )

        # RegularLesson - Регулярные уроки
        self.regular_lesson = self.Entity(
            self,
            'regular-lesson',
            filter_model=RegularLessonFilter,
            create_model=RegularLessonCreate,
            update_model=RegularLessonUpdate,
            branch_required=True
        )

        # Tariff - Тарифы абонементов
        self.tariff = self.Entity(
            self,
            'tariff',
            filter_model=TariffFilter,
            create_model=TariffCreate,
            update_model=TariffUpdate,
            branch_required=True
        )

        # Task - Задачи
        self.task = self.Entity(
            self,
            'task',
            filter_model=TaskFilter,
            create_model=TaskCreate,
            update_model=TaskUpdate,
            branch_required=True
        )

        # Teacher - Педагоги
        self.teacher = self.Entity(
            self,
            'teacher',
            filter_model=TeacherFilter,
            create_model=TeacherCreate,
            update_model=TeacherUpdate,
            branch_required=True
        )

        # TeacherRate - Ставки педагогов (специальный обработчик)
        self.teacher_rate = self.Entity(
            self,
            'teacher/teacher-rate',
            filter_model=TeacherFilter,
            create_model=TeacherCreate,
            update_model=TeacherUpdate,
            branch_required=True
        )

        # WorkingHours - График работы педагогов
        self.working_hours = self.Entity(
            self,
            'teacher/working-hour',
            filter_model=TeacherWorkingHours,
            branch_required=True
        )



        # Другие сущности инициализируются по аналогии

    def _request(self, method: str, url: str, data: Dict = None) -> Dict:
        """Базовый метод для выполнения запросов"""
        if not self.token or datetime.now() >= self.token_expires_at:
            self.authenticate()

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
        """Обработка HTTP ошибок"""
        status_code = response.status_code
        try:
            error_data = response.json()
        except ValueError:
            error_data = {}

        message = error_data.get('message', 'Unknown error')

        if status_code == 401:
            raise AuthenticationError("Invalid or expired token") from error
        elif status_code == 403:
            raise AccessDeniedError("Access denied") from error
        elif status_code == 404:
            raise NotFoundError(message) from error
        elif status_code == 429:
            raise RateLimitExceeded(message) from error
        else:
            raise APIRequestError(
                f"API request failed ({status_code}): {message}",
                status_code=status_code,
                response_data=error_data
            ) from error

    def authenticate(self):
        """Аутентификация и получение нового токена"""
        url = f"https://{self.hostname}/v2api/auth/login"

        try:
            response = requests.post(url, json={
                "email": self.email,
                "api_key": self.api_key
            })
            response.raise_for_status()

            auth_data = response.json()
            self.token = auth_data.get('token')
            if not self.token:
                raise AuthenticationError("No token in response")

            # Токен действителен 3600 секунд (1 час)
            self.token_expires_at = datetime.now() + timedelta(seconds=3500)

        except requests.HTTPError as e:
            raise AuthenticationError(f"Authentication failed: {e.response.text}") from e

    def set_branch(self, branch_id: int):
        """Установка активного филиала"""
        self.branch_id = branch_id
