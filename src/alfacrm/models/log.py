from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator, conint
import re
from .base import ALFABaseModel

class LogBase(ALFABaseModel):
    """Базовые поля записи лога"""
    entity: Optional[str] = Field(None, description="Название сущности")
    entity_id: Optional[int] = Field(None, description="ID сущности")
    user_id: Optional[int] = Field(None, description="ID автора изменений")
    event: Optional[conint(ge=1, le=3)] = Field(
        None,
        description="1-добавление, 2-восстановление, 3-удаление"
    )

class LogFilter(LogBase):
    """Фильтрация записей истории изменений"""
    date_from: Optional[str] = Field(
        None,
        description="Начальная дата (DD.MM.YYYY)"
    )
    date_to: Optional[str] = Field(
        None,
        description="Конечная дата (DD.MM.YYYY)"
    )
    page: int = Field(0, ge=0, description="Номер страницы")

    @field_validator("date_from", "date_to")
    def validate_dates(cls, v: str) -> str:
        if v and not re.match(r"^\d{2}\.\d{2}\.\d{4}$", v):
            raise ValueError("Неверный формат даты. Используйте DD.MM.YYYY")
        return v

    @field_validator("event")
    def validate_event(cls, v: int) -> int:
        if v not in (1, 2, 3):
            raise ValueError("Допустимые значения: 1, 2, 3")
        return v

class LogResponse(LogBase):
    """Полная модель записи лога"""
    id: int = Field(..., description="Уникальный идентификатор")
    fields_old: Optional[list] = Field(
        None,
        description="Значения полей до изменений"
    )
    fields_new: Optional[list] = Field(
        None,
        description="Значения полей после изменений"
    )
    fields_rel: Optional[list] = Field(
        None,
        description="Данные связанных сущностей"
    )
    date_time: str = Field(
        ...,
        pattern=r"^\d{2}\.\d{2}\.\d{4}$",
        description="Дата события (DD.MM.YYYY)"
    )

    @field_validator("date_time")
    def validate_datetime(cls, v: str) -> str:
        try:
            datetime.strptime(v, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Некорректная дата. Формат: DD.MM.YYYY")
        return v
