from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.prediction.pred import predict_silfam_price
from app.schemas.response import PredictionResponseSchema


router = APIRouter(tags=["Prediction"])


@router.get(
    "/prediction",
    response_model=PredictionResponseSchema,
)
def prediction(
    db: Session = Depends(get_db),
):
    try:
        return predict_silfam_price(db)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )