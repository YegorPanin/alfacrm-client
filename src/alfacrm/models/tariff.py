# tariff.py
from datetime import date
from typing import List, Optional, Literal
from pydantic import Field, model_validator
from .base import ALFABaseModel, DateRangeMixin

TariffType = Literal[1, 2, 3]
TariffStatus = Literal['active', 'archived']

class TariffBase(ALFABaseModel, DateRangeMixin):
    """Базовые параметры тарифного плана"""
    name: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Название тарифа"
    )
    tariff_type: TariffType = Field(
        ...,
        description="1-поурочный, 2-помесячный, 3-недельный"
    )
    subject_ids: List[int] = Field(
        default_factory=list,
        min_length=1,
        description="Привязка к предметам"
    )
    duration: Optional[int] = Field(
        None,
        gt=0,
        description="Длительность (мес/нед в зависимости от типа)"
    )
    max_lessons: Optional[int] = Field(
        None,
        gt=0,
        description="Макс. уроков для поурочного типа"
    )
    price: float = Field(..., gt=0, description="Стоимость тарифа")
    is_burnable: bool = Field(
        True,
        description="Сгораемый остаток (по умолчанию True)"
    )
    status: TariffStatus = Field('active', description="Статус тарифа")

    @model_validator(mode='after')
    def validate_type_params(self) -> 'TariffBase':
        if self.tariff_type == 1 and not self.max_lessons:
            raise ValueError("Для поурочного тарифа укажите max_lessons")
        if self.tariff_type in (2,3) and not self.duration:
            raise ValueError(f"Для типа {self.tariff_type} укажите длительность")
        return self

class TariffCreate(TariffBase):
    """Обязательные поля при создании тарифа"""
    b_date: date = Field(..., description="Дата активации тарифа")

class TariffUpdate(ALFABaseModel):
    """Поля для обновления тарифа"""
    status: Optional[TariffStatus] = None
    e_date: Optional[date] = None
    is_burnable: Optional[bool] = None

class TariffResponse(TariffBase):
    """Полный ответ системы по тарифу"""
    id: int = Field(..., description="Идентификатор тарифа")
    created_at: date = Field(..., description="Дата создания")
    updated_at: date = Field(..., description="Дата обновления")
    used_count: int = Field(..., description="Количество активаций")

class TariffFilter(ALFABaseModel, DateRangeMixin):
    """Фильтр для поиска тарифов"""
    name: Optional[str] = None
    tariff_type: Optional[TariffType] = None
    subject_id: Optional[int] = Field(None, gt=0)
    price_from: Optional[float] = None
    price_to: Optional[float] = None
    status: Optional[TariffStatus] = None
    page: int = Field(0, ge=0)
