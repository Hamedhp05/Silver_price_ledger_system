from datetime import datetime

from app.models.silver_price import PriceModel
from app.services.price_service import (
    get_chart_data,
    get_latest_price,
    get_price_history,
)


def test_get_latest_price(
    db_session,
    seed_sources,
):
    source = seed_sources[0]

    db_session.add_all(
        [
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
            ),
            PriceModel(
                source_id=source.id,
                price=260000,
                fetched_at=datetime(
                    2026,
                    8,
                    19,
                    11,
                    0,
                ),
            ),
        ]
    )

    db_session.commit()

    result = get_latest_price(db_session)

    assert result is not None
    assert result.price == 260000
    assert result.source == "tgju"


def test_get_latest_price_with_no_data(
    db_session,
    seed_sources,
):
    result = get_latest_price(db_session)

    assert result is None


def test_get_price_history(
    db_session,
    seed_sources,
):
    source = seed_sources[0]

    db_session.add_all(
        [
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
            ),
            PriceModel(
                source_id=source.id,
                price=260000,
                fetched_at=datetime(
                    2026,
                    8,
                    19,
                    11,
                    0,
                ),
            ),
        ]
    )

    db_session.commit()

    result = get_price_history(
        db_session,
        start_date=datetime(
            2026,
            8,
            19,
            0,
            0,
        ),
        end_date=datetime(
            2026,
            8,
            19,
            23,
            59,
        ),
        source="tgju",
        limit=10,
    )

    assert len(result) == 2
    assert result[0].price == 250000
    assert result[1].price == 260000


def test_get_price_history_limit(
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

    result = get_price_history(
        db_session,
        limit=2,
    )

    assert len(result) == 2


def test_get_chart_data(
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

    result = get_chart_data(
        db_session,
        point_count=3,
    )

    assert len(result) == 3

    assert result[0].price == 250004
    assert result[1].price == 250003
    assert result[2].price == 250002