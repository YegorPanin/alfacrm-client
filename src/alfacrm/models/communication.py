from datetime import datetime
from typing import Optional, Literal
from pydantic import Field, BaseModel, field_validator, model_validator
import re

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
class PhoneCallDirection(Literal[1, 2]):
    INCOMING = 1
    OUTGOING = 2

class PhoneCallFilter(ALFABaseModel):
    direction: Optional[PhoneCallDirection] = None
    is_success: Optional[bool] = None
    local_number: Optional[str] = None
    remote_number: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    page: int = Field(0, ge=0)

    @field_validator("date_from", "date_to")
    def validate_dates(cls, v: str) -> str:
        if v and not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            raise ValueError("Формат даты: YYYY-MM-DD")
        return v

class PhoneCallResponse(ALFABaseModel):
    id: int
    direction: PhoneCallDirection
    local_number: str
    remote_number: str
    duration: int
    call_date: datetime
    record_url: Optional[str]
