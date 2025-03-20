from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import date
from typing import Optional, Any


# 1. Базовые настройки для всех моделей
class ALFABaseModel(BaseModel):
    """
    Базовая модель для всех сущностей ALFA CRM.
    Настройки адаптированы для Pydantic v2.
    """
    model_config = ConfigDict(
        extra='forbid',
        json_encoders={
            date: lambda v: v.strftime('%Y-%m-%d')
        },
        use_enum_values=True,
        validate_default=True
    )


# 2. Миксин для диапазонов дат
class DateRangeMixin(ALFABaseModel):
    date_from: Optional[date] = Field(None, description="Дата начала")
    date_to: Optional[date] = Field(None, description="Дата окончания")

    @field_validator('date_to')
    @classmethod
    def validate_date_range(cls, v: Optional[date], values: dict[str, Any]) -> Optional[date]:
        if v and values.data.get('date_from') and v < values.data['date_from']:
            raise ValueError('Дата окончания должна быть >= даты начала')
        return v


# 3. Модель фильтрации клиентов
class CustomerFilter(DateRangeMixin):
    id: Optional[int] = Field(None, description="ID клиента")
    is_study: Optional[int] = Field(None, description="0-лид, 1-клиент")
    age_from: Optional[int] = Field(None, ge=0, description="Возраст от")
    age_to: Optional[int] = Field(None, ge=0, description="Возраст до")

    # ... остальные поля

    @field_validator('age_to')
    @classmethod
    def validate_age_range(cls, v: Optional[int], values: dict[str, Any]) -> Optional[int]:
        if v and values.data.get('age_from') and v < values.data['age_from']:
            raise ValueError('Максимальный возраст должен быть >= минимального')
        return v