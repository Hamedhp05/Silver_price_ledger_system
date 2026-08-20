import logging
import joblib
import pandas as pd
from sqlalchemy.orm import Session
from app.models.prediction import PredictionModel
from app.models.silver_price import PriceModel
from app.models.sources import SourceModel
from app.prediction.training import FEATURES
from app.prediction.training import LINEAR_MODEL_PATH
from app.prediction.training import RANDOM_FOREST_MODEL_PATH


logger = logging.getLogger(__name__)


def load_model(model_path):
    if not model_path.exists():
        raise FileNotFoundError(
            f"Model file not found: {model_path}"
        )

    return joblib.load(model_path)


def get_price_data(
    db: Session,
) -> pd.DataFrame:

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
                [
                    "tgju",
                    "silfam",
                    "noghresea",
                ]
            )
        )
        .order_by(
            PriceModel.fetched_at.asc()
        )
        .all()
    )

    if not data:
        raise ValueError(
            "No price data available."
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

    return df


def prepare_prediction_features(
    df: pd.DataFrame,
) -> pd.DataFrame:

    sources = {}

    for source_name in (
        "silfam",
        "tgju",
        "noghresea",
    ):
        sources[source_name] = (
            df[df["source"] == source_name]
            [["fetched_at", "price"]]
            .rename(
                columns={
                    "price": source_name
                }
            )
            .sort_values("fetched_at")
        )

    data = pd.merge_asof(
        sources["silfam"],
        sources["tgju"],
        on="fetched_at",
        direction="backward",
    )

    data = pd.merge_asof(
        data,
        sources["noghresea"],
        on="fetched_at",
        direction="backward",
    )

    data = data.dropna(
        subset=[
            "silfam",
            "tgju",
            "noghresea",
        ]
    )

    if len(data) < 6:
        raise ValueError(
            "Not enough data for prediction."
        )

    data["silver_price"] = data[
        [
            "tgju",
            "silfam",
            "noghresea",
        ]
    ].mean(axis=1)

    data["lag_1"] = (
        data["silver_price"].shift(1)
    )

    data["lag_2"] = (
        data["silver_price"].shift(2)
    )

    data["lag_3"] = (
        data["silver_price"].shift(3)
    )

    data["ma_3"] = (
        data["silver_price"]
        .rolling(3)
        .mean()
    )

    data["ma_5"] = (
        data["silver_price"]
        .rolling(5)
        .mean()
    )

    data["price_change"] = (
        data["silver_price"]
        .pct_change()
    )

    data = data.dropna()

    if data.empty:
        raise ValueError(
            "Not enough data for prediction."
        )

    return data


def _predict(
    db: Session,
    model_path,
    model_name: str,
):
    try:
        model = load_model(model_path)

        df = get_price_data(db)

        data = prepare_prediction_features(df)

        latest = data.iloc[-1]

        features = pd.DataFrame(
            [[
                latest["tgju"],
                latest["silfam"],
                latest["noghresea"],
                latest["lag_1"],
                latest["lag_2"],
                latest["lag_3"],
                latest["ma_3"],
                latest["ma_5"],
                latest["price_change"],
            ]],
            columns=FEATURES,
        )

        predicted_price = model.predict(
            features
        )[0]

        predicted_price = int(
            round(predicted_price)
        )

        prediction = PredictionModel(
            predicted_price=predicted_price,
            model=model_name
        )

        db.add(prediction)
        db.commit()
        db.refresh(prediction)

        logger.info(
            "Prediction created using %s.",
            model_name,
        )

        return {
            "predicted_price": prediction.predicted_price,
            "model": prediction.model,
            "predicted_at": prediction.predicted_at,
        }

    except Exception:
        db.rollback()

        logger.exception(
            "Prediction failed using %s.",
            model_name,
        )

        raise


def predict_linear_regression(db: Session):
    return _predict(
        db,
        LINEAR_MODEL_PATH,
        "LinearRegression",
    )


def predict_random_forest(db: Session):
    return _predict(
        db,
        RANDOM_FOREST_MODEL_PATH,
        "RandomForestRegressor",
    )