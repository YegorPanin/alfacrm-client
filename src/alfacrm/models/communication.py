from datetime import datetime
from typing import Optional, Literal
from pydantic import Field, BaseModel, field_validator, model_validator
from .base import ALFABaseModel
import re
from enum import Enum

class CommunicationBase(ALFABaseModel):
    """Базовые поля коммуникации"""
    type_id: Optional[int] = Field(
        None,
        description="Тип коммуникации: 1 - комментарий"
    )
    user_id: Optional[int] = Field(
        None,
        description="ID пользователя"
    )
    comment: Optional[str] = Field(
        None,
        max_length=2048,
        description="Текст комментария"
    )

class CommunicationCreate(ALFABaseModel):
    """Модель для создания комментария (параметры в URL + тело)"""
    comment: str = Field(..., max_length=2048)
    q_class: Literal['Customer', 'Group'] = Field(
        ...,
        alias="class",
        description="Класс связанной сущности"
    )
    related_id: int = Field(..., description="ID связанной сущности")

class CommunicationUpdate(ALFABaseModel):
    """Обновление комментария"""
    comment: str = Field(..., max_length=2048)

class CommunicationResponse(CommunicationBase):
    """Ответ с системными полями"""
    id: int
    branch_id: int
    class_name: Optional[str] = Field(
        None,
        description="Customer, Lead, Group и т.д."
    )
    related_id: Optional[int]
    added: datetime
    updated_at: Optional[datetime]

class CommunicationFilter(ALFABaseModel):
    """Фильтрация комментариев"""
    id: Optional[int] = None
    type_id: Optional[int] = None
    user_id: Optional[int] = None
    comment: Optional[str] = None
    page: int = Field(0, ge=0)

# Модели для SMS-сообщений
class SmsMessageFilter(ALFABaseModel):
    id: Optional[int] = None
    user_id: Optional[int] = None
    phone: Optional[str] = None
    is_fail: Optional[bool] = None
    is_sent: Optional[bool] = None
    is_archive: Optional[bool] = None
    added_from: Optional[str] = None
    added_to: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    page: int = Field(0, ge=0)

    @field_validator("added_from", "added_to", "date_from", "date_to")
    def validate_dates(cls, v: str) -> str:
        if v and not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            raise ValueError("Формат даты: YYYY-MM-DD")
        return v

class SmsMessageResponse(ALFABaseModel):
    id: int
    phone: str
    text: str
    is_fail: bool
    is_sent: bool
    added: datetime
    sent_date: Optional[datetime]

# Модели для Email-сообщений
class MailMessageFilter(ALFABaseModel):
    id: Optional[int] = None
    user_id: Optional[int] = None
    email: Optional[str] = None
    name: Optional[str] = None
    subject: Optional[str] = None
    is_fail: Optional[bool] = None
    is_sent: Optional[bool] = None
    is_archive: Optional[bool] = None
    added_from: Optional[str] = None
    added_to: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    page: int = Field(0, ge=0)

    @field_validator("date_from", "date_to")
    def validate_dates(cls, v: str) -> str:
        if v and not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            raise ValueError("Формат даты: YYYY-MM-DD")
        return v

class MailMessageResponse(ALFABaseModel):
    id: int
    email: str
    subject: str
    html: str
    is_sent: bool
    sent_date: Optional[datetime]

# Модели для звонков
# Решение 1: Используем Enum
class PhoneCallDirection(int, Enum):
    Incoming = 1
    Outgoing = 2

# Решение 2: Используем Literal напрямую в поле
class PhoneCallCreate(ALFABaseModel):
    """
    Модель для создания записи о телефонном звонке
    """
    phone_id: int = Field(..., description="ID контакта")
    direction: int = Field(..., ge=1, le=2, description="1-входящий, 2-исходящий")
    duration: int = Field(..., ge=0, description="Длительность в секундах")
    result_id: int = Field(..., description="ID результата из справочника")
    comment: str | None = Field(None, max_length=500)
    manager_id: int | None = Field(None, description="ID ответственного менеджера")
    branch_id: int | None = Field(None, description="ID филиала")

class PhoneCallResponse(PhoneCallCreate):
    id: int
    created_at: str  # Можно заменить на datetime при необходимости
