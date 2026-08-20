from datetime import datetime

from app.models.silver_price import PriceModel


def test_latest_price_api(
    client,
    db_session,
    seed_sources,
):
    source = seed_sources[0]

    db_session.add(
        PriceModel(
            source_id=source.id,
            price=250000,
            fetched_at=datetime(
                2026,
                8,
                19,
                10,
                0,
            ),
        )
    )

    db_session.commit()

    response = client.get(
        "/prices/latest"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["price"] == 250000
    assert data["source"] == "tgju"
    assert data["timestamp"] is not None


def test_latest_price_api_when_no_data(
    client,
):
    response = client.get(
        "/prices/latest"
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "No price data available."
    }


def test_price_history_api(
    client,
    db_session,
    seed_sources,
):
    source = seed_sources[0]

    db_session.add(
        PriceModel(
            source_id=source.id,
            price=250000,
            fetched_at=datetime(
                2026,
                8,
                19,
                10,
                0,
            ),
        )
    )

    db_session.commit()

    response = client.get(
        "/prices/history",
        params={
            "start_date": (
                "2026-08-19T00:00:00"
            ),
            "end_date": (
                "2026-08-19T23:59:59"
            ),
            "source": "tgju",
            "limit": 10,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["price"] == 250000
    assert data[0]["source_id"] == source.id


def test_price_history_limit(
    client,
    db_session,
    seed_sources,
):
    source = seed_sources[0]

    for index in range(5):
        db_session.add(
            PriceModel(
                source_id=source.id,
                price=250000 + index,
                fetched_at=datetime(
                    2026,
                    8,
                    19,
                    10,
                    index,
                ),
            )
        )

    db_session.commit()

    response = client.get(
        "/prices/history",
        params={
            "start_date": (
                "2026-08-19T00:00:00"
            ),
            "end_date": (
                "2026-08-19T23:59:59"
            ),
            "limit": 2,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2


def test_chart_api(
    client,
    db_session,
    seed_sources,
):
    source = seed_sources[1]

    for index in range(5):
        db_session.add(
            PriceModel(
                source_id=source.id,
                price=250000 + index,
                fetched_at=datetime(
                    2026,
                    8,
                    19,
                    10,
                    index,
                ),
            )
        )

    db_session.commit()

    response = client.get(
        "/prices/chart",
        params={
            "point_count": 3,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 3