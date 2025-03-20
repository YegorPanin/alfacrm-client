from datetime import date
from typing import Optional, List, Union
from pydantic import Field, field_validator, ConfigDict
from .base import ALFABaseModel, DateRangeMixin, NumericRangeMixin

class CustomerBase(ALFABaseModel):
    """Базовые поля для клиента (опциональные)"""
    name: Optional[str] = Field(None, max_length=50, description="Имя клиента")
    legal_type: Optional[int] = Field(None, ge=1, le=2, description="1-физ.лицо, 2-юр.лицо")
    is_study: Optional[int] = Field(None, ge=0, le=2, description="0-лид, 1-клиент, 2-все")
    study_status_id: Optional[int] = Field(None, description="ID статуса обучения")
    legal_name: Optional[str] = Field(None, max_length=50, description="Имя заказчика")
    company_id: Optional[int] = Field(None, description="ID компании")
    dob: Optional[date] = Field(None, description="Дата рождения")
    assigned_id: Optional[int] = Field(None, description="ID ответственного менеджера")
    employee_id: Optional[int] = Field(None, description="ID ответственного педагога")
    lead_source_id: Optional[int] = Field(None, description="ID источника лида")
    color: Optional[int] = Field(None, description="ID цвета")
    note: Optional[str] = Field(None, description="Примечание")

class CustomerCreate(CustomerBase):
    """Модель создания клиента"""
    name: str = Field(..., max_length=50, description="Имя клиента")
    legal_type: int = Field(..., ge=1, le=2, description="1-физ.лицо, 2-юр.лицо")
    is_study: int = Field(..., ge=0, le=1, description="0-лид, 1-клиент")

    # Специфичные для создания поля
    branch_ids: Optional[List[int]] = Field(None, description="ID филиалов")
    teacher_ids: Optional[List[int]] = Field(None, description="ID педагогов")
    lead_status_ids: Optional[List[int]] = Field(None, description="ID этапов воронки")
    phone: Optional[List[str]] = Field(None, description="Телефоны")
    email: Optional[List[str]] = Field(None, description="Email адреса")
    web: Optional[List[str]] = Field(None, description="Сайты")
    addr: Optional[List[str]] = Field(None, description="Адреса")

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

class CustomerUpdate(CustomerBase):
    """Модель обновления клиента"""
    balance: Optional[float] = Field(None, description="Баланс счета")
    paid_lesson_count: Optional[int] = Field(None, description="Количество оплаченных уроков")

class CustomerFilter(CustomerBase, DateRangeMixin, NumericRangeMixin):
    """Модель фильтрации клиентов"""
    id: Optional[int] = Field(None, description="ID клиента")
    gender: Optional[int] = Field(None, ge=0, le=2, description="0-не указан, 1-мужской, 2-женский")
    age_from: Optional[int] = Field(None, ge=0, le=150, description="Возраст от")
    age_to: Optional[int] = Field(None, ge=0, le=150, description="Возраст до")
    phone: Optional[str] = Field(None, description="Номер телефона")
    removed: Optional[int] = Field(None, ge=0, le=2, description="0-активные, 1-все, 2-архивные")
    level_id: Optional[int] = Field(None, description="ID уровня знаний")
    withGroups: Optional[bool] = Field(None, description="С активными группами")
    customer_reject_id: Optional[int] = Field(None, description="ID причины отказа")
    comment: Optional[str] = Field(None, description="Комментарий")
    
    # Диапазоны дат
    removed_from: Optional[date] = None
    removed_to: Optional[date] = None
    next_lesson_date_from: Optional[date] = None
    next_lesson_date_to: Optional[date] = None
    last_attend_date_from: Optional[date] = None
    last_attend_date_to: Optional[date] = None
    tariff_till_from: Optional[date] = None
    tariff_till_to: Optional[date] = None
    dob_from: Optional[date] = None
    dob_to: Optional[date] = None
    
    # Диапазоны чисел
    lesson_count_from: Optional[int] = Field(None, ge=0, description="Остаток уроков от")
    lesson_count_to: Optional[int] = Field(None, ge=0, description="Остаток уроков до")
    balance_contract_from: Optional[float] = None
    balance_contract_to: Optional[float] = None
    balance_bonus_from: Optional[float] = None
    balance_bonus_to: Optional[float] = None

    @field_validator('age_to', 'lesson_count_to', 'balance_contract_to', 'balance_bonus_to')
    @classmethod
    def validate_ranges(cls, v, values):
        field_name = values.data.get('field_name') 
        from_field = field_name.replace('_to', '_from')
        if v and values.data.get(from_field) and v < values.data[from_field]:
            raise ValueError(f"{field_name} должно быть >= {from_field}")
        return v
