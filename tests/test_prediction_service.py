import pandas as pd
import pytest

from app.services.prediction_service import (
    get_price_data,
    load_model,
    prepare_prediction_features,
)


def test_load_model_when_file_does_not_exist(
    tmp_path,
):
    model_path = tmp_path / "missing_model.pkl"

    with pytest.raises(FileNotFoundError):
        load_model(model_path)


def test_get_price_data_with_no_data(
    db_session,
):
    with pytest.raises(
        ValueError,
        match="No price data available.",
    ):
        get_price_data(db_session)


def test_prepare_prediction_features_with_not_enough_data():
    df = pd.DataFrame(
        [
            {
                "price": 250000,
                "fetched_at": pd.Timestamp(
                    "2026-08-19 10:00:00"
                ),
                "source": "tgju",
            }
        ]
    )

    with pytest.raises(
        ValueError,
        match="Not enough data for prediction.",
    ):
        prepare_prediction_features(df)