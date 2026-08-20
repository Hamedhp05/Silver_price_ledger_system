import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.request import ChartRequestSchema
from app.schemas.request import HistoricalRequestSchema
from app.schemas.response import ChartResponseSchema
from app.schemas.response import HistoricalDataSchema
from app.schemas.response import LatestPriceSchema
from app.services.price_service import get_chart_data,get_latest_price,get_price_history

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/prices",tags=["Prices"])


@router.get("/latest",response_model=LatestPriceSchema)
def latest_price(db: Session = Depends(get_db)):
    try:
        result = get_latest_price(db)

        if result is None:
            raise HTTPException(status_code=404,detail="No price data available.")

        return result

    except HTTPException:
        raise

    except Exception as exc:
        logger.exception("Failed to get latest price.")

        raise HTTPException(status_code=500,detail="Failed to get latest price.") from exc


@router.get("/history",response_model=list[HistoricalDataSchema],)
def historical_price(request: HistoricalRequestSchema = Depends(),db: Session = Depends(get_db)):
    try:
        return get_price_history(db,request.start_date,request.end_date,request.source,request.limit)

    except Exception as exc:
        logger.exception("Failed to get price history.")

        raise HTTPException(status_code=500,detail="Failed to get price history.") from exc


@router.get("/chart",response_model=list[ChartResponseSchema])
def chart_price_and_time(request: ChartRequestSchema = Depends() , db: Session = Depends(get_db),):
    try:
        return get_chart_data(db,request.point_count)

    except Exception as exc:
        logger.exception("Failed to get chart data.")

        raise HTTPException(status_code=500,detail="Failed to get chart data.") from exc