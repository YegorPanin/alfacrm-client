from typing import Optional, List, Annotated
from pydantic import BaseModel, Field, conint, model_validator, field_validator

class TariffBase(BaseModel):
    """Базовые поля абонемента"""
    type: Optional[conint(ge=1, le=3)] = Field(
        None,
        description="Тип тарифа: 1–поурочный, 2–помесячный, 3–недельный"
    )
    name: Optional[str] = Field(
        None,
        max_length=50,
        description="Название тарифа"
    )
    price: Optional[conint(ge=0)] = Field(
        None,
        description="Стоимость в копейках/центах"
    )
    lessons_count: Optional[conint(ge=1)] = Field(
        None,
        description="Количество занятий"
    )
    duration: Optional[conint(ge=1)] = Field(
        None,
        description="Длительность урока (минуты)"
    )
    branch_ids: Optional[List[int]] = Field(
        None,
        description="ID разрешенных филиалов"
    )

class TariffCreate(TariffBase):
    """Обязательные поля для создания тарифа"""
    type: conint(ge=1, le=3) = Field(...)
    name: str = Field(..., max_length=50)
    price: conint(ge=0) = Field(...)
    lessons_count: conint(ge=1) = Field(...)

class TariffUpdate(BaseModel):
    """Поля для обновления"""
    note: Optional[str] = Field(None, max_length=500, description="Примечание")

class TariffResponse(TariffBase):
    """Полный ответ с системными полями"""
    id: int
    created_at: str
    updated_at: str

class TariffFilter(BaseModel):
    """Фильтрация тарифов"""
    name: Optional[str] = None
    price_from: Optional[float] = None
    price_to: Optional[float] = None
    type: Optional[conint(ge=1, le=3)] = None
    calculation_type: Optional[conint(ge=1, le=2)] = Field(
        None,
        description="Тип расчета: 1-базовый, 2-раздельный"
    )
    is_archive: Optional[bool] = None
    lessons_count: Optional[conint(ge=1)] = None
    page: conint(ge=0) = 0

    @model_validator(mode="after")
    def validate_pricing(self) -> 'TariffFilter':
        if self.price_from and self.price_to and self.price_from > self.price_to:
            raise ValueError("price_to должно быть >= price_from")
        return self

    @field_validator("price_from", "price_to")
    def validate_price(cls, v: float) -> float:
        if v and v < 0:
            raise ValueError("Цена не может быть отрицательной")
        return v
