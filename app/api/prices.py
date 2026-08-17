from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.price_service import get_latest_price
from app.services.price_service import get_price_history
from app.services.price_service import get_chart_data

from app.schemas.response import LatestPriceSchema
from app.schemas.response import HistoricalDataSchema
from app.schemas.response import ChartResponseSchema

from app.schemas.request import HistoricalRequestSchema
from app.schemas.request import ChartRequestSchema


router = APIRouter(
    prefix="/prices",
    tags=["Prices"]
)


@router.get("/latest",response_model=LatestPriceSchema)
def latest_price(
    db: Session = Depends(get_db)
):
    return get_latest_price(db)

@router.get("/history",response_model=list[HistoricalDataSchema])
def historical_price(
    request: HistoricalRequestSchema = Depends(),
    db: Session = Depends(get_db)
):
    return get_price_history(
        db,
        request.start_date,
        request.end_date,
        request.source,
        request.limit
    )

@router.get("/chart",response_model=list[ChartResponseSchema])
def chart_price_and_time(
    request: ChartRequestSchema = Depends(),
    db: Session = Depends(get_db)
):
    return get_chart_data(
        db,
        request.point_count
    )
