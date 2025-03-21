# discount.py
from datetime import date, datetime
from typing import List, Literal, Optional
from pydantic import Field, model_validator, field_validator
from .base import ALFABaseModel
import re

DiscountType = Literal['fixed', 'percent']
DiscountStatus = Literal['active', 'archived']
DiscountApplyType = Literal['manual', 'auto']


class DiscountBase(ALFABaseModel):
    """Базовые параметры скидки"""
    name: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="Наименование скидки"
    )
    discount_type: DiscountType = Field(
        ...,
        description="Тип скидки: fixed - фиксированная, percent - процентная"
    )
    value: float = Field(
        ...,
        gt=0,
        description="Значение скидки (фиксированная сумма или процент)"
    )
    max_amount: Optional[float] = Field(
        None,
        gt=0,
        description="Максимальная сумма скидки (только для процентного типа)"
    )
    code: Optional[str] = Field(
        None,
        max_length=50,
        description="Промокод (если требуется)"
    )
    b_date: date = Field(
        ...,
        description="Дата начала действия скидки (DD.MM.YYYY)"
    )
    e_date: Optional[date] = Field(
        None,
        description="Дата окончания действия (если не указана - бессрочно)"
    )
    status: DiscountStatus = Field(
        'active',
        description="Статус: active - активна, archived - в архиве"
    )
    apply_type: DiscountApplyType = Field(
        'manual',
        description="Тип применения: manual - ручной, auto - автоматический"
    )

    # Валидация дат
    @model_validator(mode='after')
    def validate_dates(self) -> 'DiscountBase':
        if self.e_date and self.b_date > self.e_date:
            raise ValueError("Дата начала не может быть позже даты окончания")
        return self

    # Валидация типа скидки
    @model_validator(mode='after')
    def validate_discount_type(self) -> 'DiscountBase':
        if self.discount_type == 'percent' and self.value > 100:
            raise ValueError("Процентная скидка не может превышать 100%")
        if self.discount_type == 'percent' and not self.max_amount:
            raise ValueError("Для процентной скидки укажите максимальную сумму")
        return self

    # Парсинг дат из строк
    @field_validator("b_date", "e_date", mode='before')
    def parse_date(cls, v: str | date) -> date:
        if isinstance(v, str):
            if not re.match(r"\d{2}\.\d{2}\.\d{4}", v):
                raise ValueError("Неверный формат даты. Используйте DD.MM.YYYY")
            return datetime.strptime(v, "%d.%m.%Y").date()
        return v


class DiscountCreate(DiscountBase):
    """Обязательные поля для создания скидки"""
    apply_to: List[int] = Field(
        default_factory=list,
        description="ID объектов применения: клиентов, групп или тарифов"
    )


class DiscountUpdate(ALFABaseModel):
    """Поля для обновления скидки"""
    name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=255,
        description="Новое наименование"
    )
    status: Optional[DiscountStatus] = None
    e_date: Optional[date] = None
    max_amount: Optional[float] = Field(None, gt=0)


class DiscountResponse(DiscountBase):
    """Полная модель ответа API для скидки"""
    id: int = Field(..., description="Уникальный идентификатор")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата обновления")
    branch_id: int = Field(..., description="ID филиала")
    creator_id: int = Field(..., description="ID создателя")


class DiscountFilter(ALFABaseModel):
    """Фильтр для поиска скидок"""
    name: Optional[str] = None
    discount_type: Optional[DiscountType] = None
    status: Optional[DiscountStatus] = None
    apply_type: Optional[DiscountApplyType] = None
    date_from: Optional[date] = Field(
        None,
        description="Фильтр по дате создания"
    )
    date_to: Optional[date] = None
    apply_to: Optional[int] = Field(
        None,
        description="Поиск скидок, привязанных к конкретному объекту"
    )
    page: int = Field(0, ge=0)
