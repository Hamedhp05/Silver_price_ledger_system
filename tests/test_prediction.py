from datetime import datetime


def test_linear_regression_prediction_api(
    client,
    monkeypatch,
):
    def fake_prediction(db):
        return {
            "predicted_price": 250000,
            "model": "LinearRegression",
            "predicted_at": datetime(
                2026,
                8,
                19,
                12,
                0,
            ),
        }

    monkeypatch.setattr(
        "app.api.prediction.predict_linear_regression",
        fake_prediction,
    )

    response = client.get(
        "/prediction/linear_regression"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["predicted_price"] == 250000
    assert data["model"] == "LinearRegression"
    assert data["predicted_at"] is not None


def test_random_forest_prediction_api(
    client,
    monkeypatch,
):
    def fake_prediction(db):
        return {
            "predicted_price": 260000,
            "model": "RandomForestRegressor",
            "predicted_at": datetime(
                2026,
                8,
                19,
                12,
                0,
            ),
        }

    monkeypatch.setattr(
        "app.api.prediction.predict_random_forest",
        fake_prediction,
    )

    response = client.get(
        "/prediction/random_forest"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["predicted_price"] == 260000
    assert data["model"] == "RandomForestRegressor"
    assert data["predicted_at"] is not None