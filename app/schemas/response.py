from datetime import datetime
from pydantic import BaseModel, Field



class ChartResponseSchema(BaseModel):
    price: int = Field(...)
    fetched_at: datetime = Field(...)

class LatestPriceSchema(BaseModel):
    price : int = Field(...)
    source : str = Field(...)
    timestamp : datetime = Field(...)

class HistoricalDataSchema(BaseModel):
    id: int = Field(...)
    source_id: int = Field(...)
    price: int = Field(...)
    currency: str = Field(...)
    fetched_at: datetime = Field(...)
    created_at: datetime = Field(...)

class PredictionResponseSchema(BaseModel):
    predicted_price: float
    model: str
    predicted_at: datetime