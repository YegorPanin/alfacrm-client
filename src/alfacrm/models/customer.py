from datetime import date
from typing import Optional, List, Union
from pydantic import BaseModel, Field, field_validator, ConfigDict
from .base import ALFABaseModel, DateRangeMixin, NumericRangeMixin


class CustomerFilter(ALFABaseModel, DateRangeMixin, NumericRangeMixin):
    """
    Модель для фильтрации клиентов
    Все поля опциональны
    """
    id: Optional[int] = Field(None, description="ID клиента")
    is_study: Optional[int] = Field(None, ge=0, le=2, description="0-лид, 1-клиент, 2-все")
    study_status_id: Optional[int] = Field(None, description="ID статуса обучения")
    name: Optional[str] = Field(None, max_length=50, description="Имя клиента")
    gender: Optional[int] = Field(None, ge=0, le=2, description="0-не указан, 1-мужской, 2-женский")
    age_from: Optional[int] = Field(None, ge=0, le=150, description="Возраст от")
    age_to: Optional[int] = Field(None, ge=0, le=150, description="Возраст до")
    phone: Optional[str] = Field(None, description="Номер телефона")
    legal_type: Optional[int] = Field(None, ge=1, le=2, description="1-физ.лицо, 2-юр.лицо")
    legal_name: Optional[str] = Field(None, max_length=50, description="Имя заказчика")
    company_id: Optional[int] = Field(None, description="ID юр.лица")
    lesson_count_from: Optional[int] = Field(None, ge=0, description="Остаток уроков от")
    lesson_count_to: Optional[int] = Field(None, ge=0, description="Остаток уроков до")
    balance_contract_from: Optional[float] = Field(None, description="Баланс договора от")
    balance_contract_to: Optional[float] = Field(None, description="Баланс договора до")
    balance_bonus_from: Optional[float] = Field(None, description="Баланс бонусов от")
    balance_bonus_to: Optional[float] = Field(None, description="Баланс бонусов до")
    removed: Optional[int] = Field(None, ge=0, le=2, description="0-активные, 1-все, 2-архивные")
    removed_from: Optional[date] = Field(None, description="Дата архивации от")
    removed_to: Optional[date] = Field(None, description="Дата архивации до")
    level_id: Optional[int] = Field(None, description="ID уровня знаний")
    assigned_id: Optional[int] = Field(None, description="ID ответственного менеджера")
    employee_id: Optional[int] = Field(None, description="ID ответственного педагога")
    lead_source_id: Optional[int] = Field(None, description="ID источника лида")
    color: Optional[int] = Field(None, description="ID цвета")
    note: Optional[str] = Field(None, description="Примечание")
    date_from: Optional[date] = Field(None, description="Дата создания от")
    date_to: Optional[date] = Field(None, description="Дата создания до")
    next_lesson_date_from: Optional[date] = Field(None, description="Дата след.урока от")
    next_lesson_date_to: Optional[date] = Field(None, description="Дата след.урока до")
    last_attend_date_from: Optional[date] = Field(None, description="Дата последнего посещения от")
    last_attend_date_to: Optional[date] = Field(None, description="Дата последнего посещения до")
    tariff_till_from: Optional[date] = Field(None, description="Срок действия абонемента от")
    tariff_till_to: Optional[date] = Field(None, description="Срок действия абонемента до")
    customer_reject_id: Optional[int] = Field(None, description="ID причины отказа")
    comment: Optional[str] = Field(None, description="Комментарий")
    dob_from: Optional[date] = Field(None, description="Дата рождения от")
    dob_to: Optional[date] = Field(None, description="Дата рождения до")
    withGroups: Optional[bool] = Field(None, description="С активными группами")
    updated_at_from: Optional[date] = Field(None, description="Дата изменения от")
    updated_at_to: Optional[date] = Field(None, description="Дата изменения до")
    created_at_from: Optional[date] = Field(None, description="Дата создания от")
    created_at_to: Optional[date] = Field(None, description="Дата создания до")

    # Валидаторы диапазонов
    @field_validator('age_to', 'lesson_count_to', 'balance_contract_to', 'balance_bonus_to')
    @classmethod
    def validate_ranges(cls, v, values):
        field = cls.model_fields[values['field_name']]
        from_field = field.name.replace('_to', '_from')
        if v and values.data.get(from_field) and v < values.data[from_field]:
            raise ValueError(f"{field.name} должно быть >= {from_field}")
        return v


class CustomerCreate(ALFABaseModel):
    """
    Модель для создания клиента
    Обязательные поля: name, legal_type, is_study
    """
    name: str = Field(..., max_length=50, description="Имя клиента")
    legal_type: int = Field(..., ge=1, le=2, description="1-физ.лицо, 2-юр.лицо")
    is_study: int = Field(..., ge=0, le=1, description="0-лид, 1-клиент")

    # Необязательные поля
    branch_ids: Optional[List[int]] = Field(None, description="ID филиалов")
    teacher_ids: Optional[List[int]] = Field(None, description="ID педагогов")
    study_status_id: Optional[int] = Field(None, description="ID статуса обучения")
    lead_status_ids: Optional[List[int]] = Field(None, description="ID этапов воронки")
    lead_source_id: Optional[int] = Field(None, description="ID источника")
    assigned_id: Optional[int] = Field(None, description="ID менеджера")
    legal_name: Optional[str] = Field(None, max_length=50, description="Имя заказчика")
    company_id: Optional[int] = Field(None, description="ID компании")
    dob: Optional[date] = Field(None, description="Дата рождения")
    phone: Optional[List[str]] = Field(None, description="Телефоны")
    email: Optional[List[str]] = Field(None, description="Email адреса")
    web: Optional[List[str]] = Field(None, description="Сайты")
    addr: Optional[List[str]] = Field(None, description="Адреса")
    note: Optional[str] = Field(None, description="Примечание")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Иванов Иван",
                "legal_type": 1,
                "is_study": 1,
                "phone": ["+79991234567"],
                "email": ["ivan@mail.ru"]
            }
        }
    )


class CustomerUpdate(ALFABaseModel):
    """
    Модель для обновления клиента
    Все поля опциональны
    """
    name: Optional[str] = Field(None, max_length=50, description="Имя клиента")
    legal_type: Optional[int] = Field(None, ge=1, le=2, description="Тип клиента")
    is_study: Optional[int] = Field(None, ge=0, le=1, description="Статус клиента")
    study_status_id: Optional[int] = Field(None, description="ID статуса обучения")
    lead_status_ids: Optional[List[int]] = Field(None, description="ID этапов воронки")
    lead_source_id: Optional[int] = Field(None, description="ID источника")
    assigned_id: Optional[int] = Field(None, description="ID менеджера")
    legal_name: Optional[str] = Field(None, max_length=50, description="Имя заказчика")
    company_id: Optional[int] = Field(None, description="ID компании")
    dob: Optional[date] = Field(None, description="Дата рождения")
    phone: Optional[List[str]] = Field(None, description="Телефоны")
    email: Optional[List[str]] = Field(None, description="Email адреса")
    web: Optional[List[str]] = Field(None, description="Сайты")
    addr: Optional[List[str]] = Field(None, description="Адреса")
    note: Optional[str] = Field(None, description="Примечание")
    balance: Optional[float] = Field(None, description="Баланс счета")
    paid_lesson_count: Optional[int] = Field(None, description="Количество оплаченных уроков")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "phone": ["+79991234567"],
                "email": ["new_email@mail.ru"],
                "balance": 1500.50
            }
        }
    )