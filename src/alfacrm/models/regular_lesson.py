from pydantic import Field
from datetime import date
from .base import ALFABaseModel

class DateRangeMixin(ALFABaseModel):
    """Миксин для работы с датами"""
    b_date: date = Field(..., description="Дата начала")
    e_date: date | None = Field(None, description="Дата окончания")

class RegularLessonBase(ALFABaseModel):
    teacher_ids: list[int] = Field(...)
    subject_id: int = Field(...)
    days_of_week: list[int] = Field(..., ge=0, le=6)
    time_from: str = Field(..., pattern=r'^\d{2}:\d{2}$')
    time_to: str = Field(..., pattern=r'^\d{2}:\d{2}$')
    branch_id: int = Field(...)
    comment: str | None = None

class RegularLessonCreate(DateRangeMixin, RegularLessonBase):
    pass

class RegularLessonResponse(DateRangeMixin, RegularLessonBase):
    id: int
    is_deleted: bool
