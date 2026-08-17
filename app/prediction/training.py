from pathlib import Path

import joblib
import pandas as pd
from sklearn.linear_model import LinearRegression
from sqlalchemy.orm import Session

from app.models.silver_price import PriceModel
from app.models.sources import SourceModel


MODEL_PATH = (
    Path(__file__).resolve().parent
    / "silfam_model.pkl"
)


def train_silfam_model(db: Session):
    data = (
        db.query(
            PriceModel.price,
            PriceModel.fetched_at,
            SourceModel.name.label("source"),
        )
        .join(
            SourceModel,
            PriceModel.source_id == SourceModel.id,
        )
        .filter(
            SourceModel.name.in_(
                ["tgju", "silfam", "noghresea"]
            )
        )
        .order_by(PriceModel.fetched_at.asc())
        .all()
    )

    if len(data) < 10:
        raise ValueError(
            "Not enough data for training"
        )

    df = pd.DataFrame(
        data,
        columns=[
            "price",
            "fetched_at",
            "source",
        ],
    )

    df["price"] = df["price"].astype(float)
    df["fetched_at"] = pd.to_datetime(
        df["fetched_at"]
    )

    silfam = (
        df[df["source"] == "silfam"]
        [["fetched_at", "price"]]
        .rename(columns={"price": "silfam"})
        .sort_values("fetched_at")
    )

    tgju = (
        df[df["source"] == "tgju"]
        [["fetched_at", "price"]]
        .rename(columns={"price": "tgju"})
        .sort_values("fetched_at")
    )

    noghresea = (
        df[df["source"] == "noghresea"]
        [["fetched_at", "price"]]
        .rename(columns={"price": "noghresea"})
        .sort_values("fetched_at")
    )

    training_data = pd.merge_asof(
        silfam,
        tgju,
        on="fetched_at",
        direction="backward",
    )

    training_data = pd.merge_asof(
        training_data,
        noghresea,
        on="fetched_at",
        direction="backward",
    )

    training_data = training_data.dropna(
        subset=[
            "silfam",
            "tgju",
            "noghresea",
        ]
    )

    if len(training_data) < 5:
        raise ValueError(
            "Not enough complete data for training"
        )

    X = training_data[
        ["tgju", "noghresea"]
    ].astype(float)

    y = training_data["silfam"].astype(float)

    model = LinearRegression()
    model.fit(X, y)

    MODEL_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(model, MODEL_PATH)

    return model