from app.scheduler import scheduler as scheduler_module


def test_run_collection_job_success(
    monkeypatch,
):
    called = False

    def fake_collect_prices():
        nonlocal called
        called = True

    monkeypatch.setattr(
        scheduler_module,
        "collect_prices",
        fake_collect_prices,
    )

    scheduler_module.run_collection_job()

    assert called is True


def test_run_collection_job_handles_exception(
    monkeypatch,
):
    def fake_collect_prices():
        raise Exception(
            "Collection failed"
        )

    monkeypatch.setattr(
        scheduler_module,
        "collect_prices",
        fake_collect_prices,
    )

    scheduler_module.run_collection_job()