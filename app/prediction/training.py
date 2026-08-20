import logging
from pathlib import Path
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from sqlalchemy.orm import Session
from app.models.silver_price import PriceModel
from app.models.sources import SourceModel


logger = logging.getLogger(__name__)


MODEL_DIR = Path(__file__).resolve().parent / "models"

LINEAR_MODEL_PATH = (MODEL_DIR / "linear_regression.pkl")

RANDOM_FOREST_MODEL_PATH = (MODEL_DIR / "random_forest.pkl")


FEATURES = [
    "tgju",
    "silfam",
    "noghresea",
    "lag_1",
    "lag_2",
    "lag_3",
    "ma_3",
    "ma_5",
    "price_change"]


def get_price_data(db: Session) -> pd.DataFrame:
    data = db.query(PriceModel.price,PriceModel.fetched_at,SourceModel.name.label("source")).join(SourceModel,PriceModel.source_id == SourceModel.id).filter(SourceModel.name.in_(["tgju", "silfam", "noghresea"])).order_by(PriceModel.fetched_at.asc()).all()


    if len(data) < 20:
        raise ValueError(
            "Not enough data for training."
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


def prepare_training_data(
    df: pd.DataFrame,
) -> pd.DataFrame:

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

    if len(training_data) < 10:
        raise ValueError(
            "Not enough complete data for training."
        )

    training_data["silver_price"] = (
        training_data[
            [
                "tgju",
                "silfam",
                "noghresea",
            ]
        ].mean(axis=1)
    )

    training_data["lag_1"] = (
        training_data["silver_price"].shift(1)
    )

    training_data["lag_2"] = (
        training_data["silver_price"].shift(2)
    )

    training_data["lag_3"] = (
        training_data["silver_price"].shift(3)
    )

    training_data["ma_3"] = (
        training_data["silver_price"]
        .rolling(3)
        .mean()
    )

    training_data["ma_5"] = (
        training_data["silver_price"]
        .rolling(5)
        .mean()
    )

    training_data["price_change"] = (
        training_data["silver_price"].pct_change()
    )

    training_data["next_price"] = (
        training_data["silver_price"].shift(-1)
    )

    training_data = training_data.dropna()

    if len(training_data) < 10:
        raise ValueError(
            "Not enough data after feature engineering."
        )

    return training_data


def evaluate_model(
    model,
    X_test,
    y_test,
):
    predictions = model.predict(X_test)

    mae = mean_absolute_error(
        y_test,
        predictions,
    )

    rmse = mean_squared_error(
        y_test,
        predictions,
    ) ** 0.5

    return mae, rmse


def train_models(db: Session):
    logger.info("Model training started.")

    try:
        df = get_price_data(db)

        training_data = prepare_training_data(df)

        split_index = int(
            len(training_data) * 0.8
        )

        train_data = training_data.iloc[
            :split_index
        ]

        test_data = training_data.iloc[
            split_index:
        ]

        X_train = train_data[FEATURES]
        y_train = train_data["next_price"]

        X_test = test_data[FEATURES]
        y_test = test_data["next_price"]

        linear_model = LinearRegression()

        linear_model.fit(
            X_train,
            y_train,
        )

        random_forest_model = RandomForestRegressor(
            n_estimators=100,
            random_state=42,
        )

        random_forest_model.fit(
            X_train,
            y_train,
        )

        linear_mae, linear_rmse = evaluate_model(
            linear_model,
            X_test,
            y_test,
        )

        forest_mae, forest_rmse = evaluate_model(
            random_forest_model,
            X_test,
            y_test,
        )

        logger.info(
            "Linear Regression - MAE: %.2f, RMSE: %.2f",
            linear_mae,
            linear_rmse,
        )

        logger.info(
            "Random Forest - MAE: %.2f, RMSE: %.2f",
            forest_mae,
            forest_rmse,
        )

        MODEL_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        joblib.dump(
            linear_model,
            LINEAR_MODEL_PATH,
        )

        joblib.dump(
            random_forest_model,
            RANDOM_FOREST_MODEL_PATH,
        )

        logger.info(
            "Models saved successfully."
        )

        return {
            "linear_model": linear_model,
            "random_forest_model": random_forest_model,
            "linear_mae": linear_mae,
            "linear_rmse": linear_rmse,
            "random_forest_mae": forest_mae,
            "random_forest_rmse": forest_rmse,
        }

    except Exception:
        logger.exception(
            "Model training failed."
        )
        raise