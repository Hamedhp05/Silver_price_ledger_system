def test_run_collector_api(
    client,
    monkeypatch,
):
    called = False

    def fake_collect_prices():
        nonlocal called
        called = True

    monkeypatch.setattr(
        "app.api.collector.collect_prices",
        fake_collect_prices,
    )

    response = client.post(
        "/collector/run"
    )

    assert response.status_code == 200

    assert response.json() == {
        "message": (
            "Price collection completed successfully."
        )
    }

    assert called is True


def test_run_collector_api_when_collection_fails(
    client,
    monkeypatch,
):
    def fake_collect_prices():
        raise Exception(
            "Collection failed"
        )

    monkeypatch.setattr(
        "app.api.collector.collect_prices",
        fake_collect_prices,
    )

    response = client.post(
        "/collector/run"
    )

    assert response.status_code == 500

    assert response.json() == {
        "detail": "Price collection failed."
    }