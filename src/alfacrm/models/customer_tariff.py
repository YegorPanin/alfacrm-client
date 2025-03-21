from datetime import datetime, date
from typing import Optional, List, Union, Annotated
from pydantic import Field, field_validator, model_validator, BeforeValidator
from .base import ALFABaseModel
import re

# Вспомогательная функция для валидации balance
def validate_balance(v: Union[int, List[int]]) -> Union[int, List[int]]:
    if isinstance(v, list):
        if len(v) != 2:
            raise ValueError("Диапазон баланса должен содержать 2 значения [from, to]")
        if v[0] > v[1]:
            raise ValueError("Начало диапазона не может превышать конец")
        if any(not isinstance(num, int) for num in v):
            raise TypeError("Значения диапазона должны быть целыми числами")
    elif v is not None and not isinstance(v, int):
        raise TypeError("Баланс должен быть целым числом")
    return v

class CustomerTariffBase(ALFABaseModel):
    """Базовые поля абонемента клиента"""
    tariff_id: Optional[int] = Field(
        default=None,
        gt=0,
        description="ID тарифа из справочника абонементов"
    )
    subject_ids: Optional[List[int]] = Field(
        default=None,
        description="Список ID предметов (если применимо)"
    )
    lesson_type_ids: Optional[List[int]] = Field(
        default=None,
        description="Список ID типов уроков (1-индивидуальный, 2-групповой и т.д.)"
    )
    is_separate_balance: Optional[bool] = Field(
        default=None,
        description="Раздельный баланс для групповых занятий"
    )
    balance: Optional[Annotated[
        Union[int, List[int]],
        BeforeValidator(validate_balance)
    ]] = Field(
        default=None,
        ge=0,
        description="Текущий баланс (число или диапазон [от, до])"
    )
    b_date: Optional[date] = Field(
        default=None,
        description="Дата начала действия в формате DD.MM.YYYY"
    )
    e_date: Optional[date] = Field(
        default=None,
        description="Дата окончания действия в формате DD.MM.YYYY"
    )
    note: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Произвольный комментарий"
    )

    @field_validator("b_date", "e_date", mode="before")
    @classmethod
    def parse_dates(cls, v: Union[str, date]) -> date:
        if isinstance(v, str):
            if not re.match(r"\d{2}\.\d{2}\.\d{4}", v):
                raise ValueError("Неверный формат даты. Используйте DD.MM.YYYY")
            return datetime.strptime(v, "%d.%m.%Y").date()
        return v

    @model_validator(mode="after")
    def check_dates_order(self) -> 'CustomerTariffBase':
        if self.b_date and self.e_date and self.b_date > self.e_date:
            raise ValueError("Дата начала не может быть позже даты окончания")
        return self

class CustomerTariffCreate(CustomerTariffBase):
    """Обязательные поля для создания абонемента"""
    tariff_id: int = Field(..., gt=0)
    customer_id: int = Field(..., gt=0, description="ID клиента в системе")
    balance: int = Field(..., ge=0)

class CustomerTariffUpdate(ALFABaseModel):
    """Поля для обновления абонемента"""
    note: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Обновление комментария к абонементу"
    )
    balance: Optional[int] = Field(
        default=None,
        ge=0,
        description="Обновление текущего баланса"
    )

class CustomerTariffResponse(CustomerTariffBase):
    """Полная модель ответа с системными полями"""
    id: int = Field(..., description="Уникальный идентификатор записи")
    customer_id: int = Field(..., description="Ссылка на клиента")
    created_at: date = Field(..., description="Дата создания записи")
    updated_at: date = Field(..., description="Дата последнего обновления")

class CustomerTariffFilter(ALFABaseModel):
    """Фильтр для поиска абонементов клиента"""
    id: Optional[int] = Field(default=None, gt=0)
    customer_id: Optional[int] = Field(default=None, gt=0)
    tariff_id: Optional[int] = Field(default=None, gt=0)
    is_burnable_out: Optional[bool] = Field(
        default=None,
        description="Фильтр по сгораемым остаткам"
    )
    balance: Optional[Annotated[
        Union[int, List[int]],
        BeforeValidator(validate_balance)
    ]] = Field(default=None)
    dead: Optional[bool] = Field(
        default=None,
        description="True - только архивные, False - активные"
    )
    tariff_type: Optional[int] = Field(
        default=None,
        ge=1,
        le=3,
        json_schema_extra={
            "description": "Тип тарифа: 1-поурочный, 2-помесячный, 3-недельный"
        }
    )
    is_separate_balance: Optional[bool] = None
    page: int = Field(default=0, ge=0)

class CustomerTariffDeleteParams(ALFABaseModel):
    """Параметры для удаления абонемента"""
    id: int = Field(..., gt=0)
    customer_id: int = Field(..., gt=0)
