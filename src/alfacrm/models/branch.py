from typing import Optional
from pydantic import Field
from .base import ALFABaseModel

class MetaBranch(ALFABaseModel):
    name: Optional[str] = Field(None, max_length=50, description="Наименование")
    is_active: Optional[int] = Field(None, ge=0, le=1, description="Флаг активности")
    subject_ids: Optional[list] = Field(None, description="Массив идентификаторов предметов")


class BranchFilter(MetaBranch):
    id: Optional[int] = Field(None, description="ID филиала")

class BranchCreate(MetaBranch):
    pass

class BranchUpdate(MetaBranch):
    pass