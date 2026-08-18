from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.response import (
    PredictionResponseSchema,
)
from app.services.prediction_service import (
    predict_linear_regression,
    predict_random_forest,
)


router = APIRouter(
    prefix="/prediction",
    tags=["Prediction"]
)


@router.get(
    "/linear_regression",
    response_model=PredictionResponseSchema,
)
def predict_linear(
    db: Session = Depends(get_db),
):
    try:
        return predict_linear_regression(db)

    except (
        ValueError,
        FileNotFoundError,
    ) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.get(
    "/random_forest",
    response_model=PredictionResponseSchema,
)
def predict_random_forest_price(
    db: Session = Depends(get_db),
):
    try:
        return predict_random_forest(db)

    except (
        ValueError,
        FileNotFoundError,
    ) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )