import pytest
from datetime import datetime
from app.collectors.normalization import NormalizationError
from app.collectors.normalization import normalize_price_data


def test_normalize_tgju_price_data():
    data = {
        "source": "tgju",
        "price": "4,074,300",
        "fetched_at": "2026-08-19 12:30:00",
    }

    result = normalize_price_data(data)

    assert result["source"] == "tgju"
    assert result["price"] == 407430
    assert result["fetched_at"].year == 2026
    assert result["fetched_at"].month == 8
    assert result["fetched_at"].day == 19


def test_normalize_silfam_price_data():
    data = {
        "source": "silfam",
        "price": "2,500,000",
        "fetched_at": "۱۹ مرداد ۱۴۰۵ ساعت ۱۰:۳۰",
    }

    result = normalize_price_data(data)

    assert result["source"] == "silfam"
    assert result["price"] == 2500000
    assert result["fetched_at"] is not None


def test_normalize_noghresea_price_data():
    data = {
        "source": "noghresea",
        "price": "2,500,000",
        "fetched_at": "۲۸ مرداد ۱۴۰۵ - ۱۵:۴۴:۰۳"
    }

    result = normalize_price_data(data)

    assert result["source"] == "noghresea"
    assert result["price"] == 2500000
    assert isinstance(result["fetched_at"], datetime)


def test_normalize_invalid_price():
    data = {
        "source": "tgju",
        "price": "invalid",
        "fetched_at": "2026-08-19 12:30:00",
    }

    with pytest.raises(NormalizationError):
        normalize_price_data(data)


def test_normalize_negative_price():
    data = {
        "source": "tgju",
        "price": "-1000",
        "fetched_at": "2026-08-19 12:30:00",
    }

    with pytest.raises(NormalizationError):
        normalize_price_data(data)


def test_normalize_missing_source():
    data = {
        "price": "250000",
        "fetched_at": "2026-08-19 12:30:00",
    }

    with pytest.raises(NormalizationError):
        normalize_price_data(data)


def test_normalize_missing_price():
    data = {
        "source": "tgju",
        "fetched_at": "2026-08-19 12:30:00",
    }

    with pytest.raises(NormalizationError):
        normalize_price_data(data)


def test_normalize_missing_fetched_at():
    data = {
        "source": "tgju",
        "price": "250000",
    }

    with pytest.raises(NormalizationError):
        normalize_price_data(data)