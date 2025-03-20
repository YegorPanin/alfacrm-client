from datetime import date
from typing import Optional
from pydantic import Field, field_validator, model_validator
from .base import ALFABaseModel

class CGIBase(ALFABaseModel):
    """Базовые поля для связи клиент-группа"""
    customer_id: int = Field(..., description="ID клиента")
    group_id: int = Field(..., description="ID группы")
    b_date: str = Field(..., description="Дата начала (DD.MM.YYYY)")
    e_date: str = Field(..., description="Дата окончания (DD.MM.YYYY)")
    branch_id: int = Field(..., description="ID филиала")

    @field_validator("b_date", "e_date")
    def validate_dates_format(cls, v: str) -> str:
        if not re.match(r"^\d{2}\.\d{2}\.\d{4}$", v):
            raise ValueError("Неверный формат даты. Используйте DD.MM.YYYY")
        return v

    @model_validator(mode="after")
    def validate_date_range(self) -> 'CGIBase':
        b_date = datetime.strptime(self.b_date, "%d.%m.%Y")
        e_date = datetime.strptime(self.e_date, "%d.%m.%Y")
        
        if e_date < b_date:
            raise ValueError("Дата окончания не может быть раньше даты начала")
        return self

class CGICreate(CGIBase):
    """Модель для создания связи"""
    pass

class CGIUpdate(ALFABaseModel):
    """Модель для обновления связи (все поля опциональны)"""
    b_date: Optional[str] = None
    e_date: Optional[str] = None
    branch_id: Optional[int] = None

    @field_validator("b_date", "e_date")
    def validate_dates_if_present(cls, v: str | None) -> str | None:
        if v and not re.match(r"^\d{2}\.\d{2}\.\d{4}$", v):
            raise ValueError("Неверный формат даты. Используйте DD.MM.YYYY")
        return v

class CGIResponse(CGIBase):
    """Модель ответа с read-only полями"""
    id: int = Field(..., description="Уникальный идентификатор связи")

class CGIGroupFilter(ALFABaseModel):
    """Фильтр для получения клиентов группы"""
    b_date: Optional[str] = None
    e_date: Optional[str] = None
    page: int = Field(0, ge=0)

    @field_validator("b_date", "e_date")
    def validate_filter_dates(cls, v: str | None) -> str | None:
        if v and not re.match(r"^\d{2}\.\d{2}\.\d{4}$", v):
            raise ValueError("Формат даты: DD.MM.YYYY")
        return v

class CGICustomerFilter(ALFABaseModel):
    """Фильтр для получения групп клиента"""
    b_date: Optional[str] = None
    e_date: Optional[str] = None
    page: int = Field(0, ge=0)

    @field_validator("b_date", "e_date")
    def validate_filter_dates(cls, v: str | None) -> str | None:
        if v and not re.match(r"^\d{2}\.\d{2}\.\d{4}$", v):
            raise ValueError("Формат даты: DD.MM.YYYY")
        return v
