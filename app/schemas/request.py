from datetime import datetime
from datetime import timedelta
from enum import Enum

from pydantic import BaseModel, Field


class SourceEnum(str, Enum):
    TGJU = "tgju"
    SILFAM = "silfam"
    NOGHRESEA = "noghresea"


class HistoricalRequestSchema(BaseModel):
    start_date: datetime = Field(default_factory=lambda: datetime.now() - timedelta(days=1) , examples=["2026-08-16T12:00:00"])
    end_date: datetime = Field(default_factory=datetime.now() , examples=["2026-08-17T12:00:00"])
    source: SourceEnum | None = None
    limit: int = Field(10, ge=1)
    

class ChartRequestSchema(BaseModel):
    point_count : int = Field(50,ge=1)
