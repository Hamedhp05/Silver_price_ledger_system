from app.collectors import price_collector


def test_collect_prices_continues_when_one_source_fails(
    db_session,
    seed_sources,
    monkeypatch,
):
    calls = []

    def fake_tgju():
        calls.append("tgju")
        raise Exception("TGJU failed")

    def fake_silfam():
        calls.append("silfam")

        return {
            "source": "silfam",
            "price": "250000",
            "fetched_at": (
                "۱۹ مرداد ۱۴۰۵ ساعت ۱۰:۳۰"
            ),
        }

    def fake_noghresea():
        calls.append("noghresea")

        return {
            "source": "noghresea",
            "price": "260000",
            "fetched_at": (
                "۱۹ مرداد ۱۴۰۵ ساعت ۱۰:۳۱"
            ),
        }

    monkeypatch.setitem(
        price_collector.SCRAPERS,
        "tgju",
        fake_tgju,
    )

    monkeypatch.setitem(
        price_collector.SCRAPERS,
        "silfam",
        fake_silfam,
    )

    monkeypatch.setitem(
        price_collector.SCRAPERS,
        "noghresea",
        fake_noghresea,
    )

    monkeypatch.setattr(
        price_collector,
        "sessionlocal",
        lambda: db_session,
    )

    price_collector.collect_prices()

    assert "tgju" in calls
    assert "silfam" in calls
    assert "noghresea" in calls