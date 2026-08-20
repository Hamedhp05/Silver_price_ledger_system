from unittest.mock import Mock

import pytest
import requests

from app.scrapers.noghresea import (
    NoghrehSeaScraperError,
    get_silver_price as get_noghresea_price,
)
from app.scrapers.silfam import (
    SilfamScraperError,
    get_silver_price as get_silfam_price,
)
from app.scrapers.tgju import (
    TGJUScraperError,
    get_silver_price as get_tgju_price,
)


def test_tgju_scraper_success(monkeypatch):
    response = Mock()

    response.raise_for_status.return_value = None

    response.json.return_value = {
        "current": {
            "silver_999": {
                "p": "4,074,300",
                "ts": "2026-08-19 12:30:00",
            }
        }
    }

    monkeypatch.setattr(
        "app.scrapers.tgju.requests.get",
        lambda *args, **kwargs: response,
    )

    result = get_tgju_price()

    assert result["source"] == "tgju"
    assert result["price"] == "4,074,300"
    assert (
        result["fetched_at"]
        == "2026-08-19 12:30:00"
    )


def test_tgju_scraper_network_error(
    monkeypatch,
):
    def fake_get(*args, **kwargs):
        raise requests.RequestException(
            "Connection failed"
        )

    monkeypatch.setattr(
        "app.scrapers.tgju.requests.get",
        fake_get,
    )

    with pytest.raises(
        TGJUScraperError
    ):
        get_tgju_price()


def test_silfam_scraper_success(monkeypatch):
    response = Mock()

    response.raise_for_status.return_value = None

    response.text = """
    <span class="silver-value">
        2,500,000
    </span>

    <div class="silver-last-update">
        ۱۹ مرداد ۱۴۰۵ ساعت ۱۰:۳۰
    </div>
    """

    monkeypatch.setattr(
        "app.scrapers.silfam.requests.get",
        lambda *args, **kwargs: response,
    )

    result = get_silfam_price()

    assert result["source"] == "silfam"
    assert result["price"] == "2,500,000"
    assert result["currency"] == "IRT"


def test_silfam_scraper_network_error(
    monkeypatch,
):
    def fake_get(*args, **kwargs):
        raise requests.RequestException(
            "Connection failed"
        )

    monkeypatch.setattr(
        "app.scrapers.silfam.requests.get",
        fake_get,
    )

    with pytest.raises(
        SilfamScraperError
    ):
        get_silfam_price()


def test_noghresea_scraper_success(
    monkeypatch,
):
    response = Mock()

    response.raise_for_status.return_value = None

    response.text = """
    <span class="
        text-gray-900
        text-subtitle2Bold
        sm:text-subtitle3Bold
    ">
        2,500,000
    </span>

    <span class="
        text-caption1Medium
        text-gray-500
        mb-4
        sm:hidden
    ">
        ۱۹ مرداد ۱۴۰۵ ساعت ۱۰:۳۰
    </span>
    """

    monkeypatch.setattr(
        "app.scrapers.noghresea.requests.get",
        lambda *args, **kwargs: response,
    )

    result = get_noghresea_price()

    assert result["source"] == "noghresea"
    assert result["price"] == "2,500,000"
    assert result["currency"] == "IRT"


def test_noghresea_scraper_network_error(
    monkeypatch,
):
    def fake_get(*args, **kwargs):
        raise requests.RequestException(
            "Connection failed"
        )

    monkeypatch.setattr(
        "app.scrapers.noghresea.requests.get",
        fake_get,
    )

    with pytest.raises(
        NoghrehSeaScraperError
    ):
        get_noghresea_price()