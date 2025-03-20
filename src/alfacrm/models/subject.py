from typing import Optional
from pydantic import Field, BaseModel
from .base import ALFABaseModel

class SubjectBase(ALFABaseModel):
    """Базовые поля предмета (опциональны для обновления)"""
    name: Optional[str] = Field(
        None,
        max_length=50,
        description="Название предмета"
    )

class SubjectCreate(SubjectBase):
    """Обязательные поля для создания предмета"""
    name: str = Field(..., max_length=50)

class SubjectUpdate(SubjectBase):
    """Поля для обновления (все опциональны)"""
    pass

class SubjectResponse(SubjectBase):
    """Ответ API с идентификатором"""
    id: int = Field(..., description="Уникальный ID предмета")

class SubjectFilter(ALFABaseModel):
    """Фильтр для метода index"""
    id: Optional[int] = Field(None, description="Фильтр по ID")
    name: Optional[str] = Field(None, description="Поиск по названию")
    active: Optional[bool] = Field(
        None,
        description="True - только активные, False - все"
    )
    page: int = Field(
        default=0,
        ge=0,
        description="Номер страницы (отсчет с 0)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "page": 0
            }
        }
    )
