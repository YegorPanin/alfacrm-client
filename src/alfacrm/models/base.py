from datetime import date
from pydantic import BaseModel, ConfigDict, field_validator
from typing import Any, Optional

class ALFABaseModel(BaseModel):
    """
    Базовая модель для всех сущностей с настройками:
    - Запрет неизвестных полей
    - Автоматическое преобразование дат в строки
    """
    model_config = ConfigDict(
        extra='forbid',
        json_encoders={
            date: lambda v: v.strftime('%Y-%m-%d')
        }
    )

class DateRangeMixin(ALFABaseModel):
    """
    Миксин для проверки диапазонов дат
    """
    date_from: Optional[date] = None
    date_to: Optional[date] = None

    @field_validator('date_to')
    @classmethod
    def validate_date_range(cls, v: Optional[date], values: dict[str, Any]) -> Optional[date]:
        if v and (date_from := values.data.get('date_from')) and v < date_from:
            raise ValueError('date_to must be >= date_from')
        return v

class NumericRangeMixin(ALFABaseModel):
    """
    Миксин для проверки числовых диапазонов
    """
    value_from: Optional[float] = None
    value_to: Optional[float] = None

    @field_validator('value_to')
    @classmethod
    def validate_numeric_range(cls, v: Optional[float], values: dict[str, Any]) -> Optional[float]:
        if v and (value_from := values.data.get('value_from')) and v < value_from:
            raise ValueError('value_to must be >= value_from')
        return v