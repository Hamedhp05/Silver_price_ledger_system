from datetime import datetime

from app.collectors.normalization import normalize_price_data
from app.database.session import sessionlocal
from app.models.silver_price import PriceModel
from app.models.sources import SourceModel
from app.scrapers.tgju import get_silver_price as get_tgju_price
from app.scrapers.silfam import get_silver_price as get_silfam_price
from app.scrapers.noghresea import get_silver_price as get_noghresea_price


SCRAPERS = {
    "tgju": get_tgju_price,
    "silfam": get_silfam_price,
    "noghresea": get_noghresea_price,
}


def collect_prices():
    db = sessionlocal()

    try:
        for source_name, scraper in SCRAPERS.items():

            source = (
                db.query(SourceModel)
                .filter_by(
                    name=source_name,
                    enabled=True,
                )
                .first()
            )

            if source is None:
                continue

            raw_data = scraper()
            data = normalize_price_data(raw_data)

            price = PriceModel(
                source_id=source.id,
                price=data["price"],
                currency=data["currency"],
                fetched_at=data["fetched_at"],
            )

            db.add(price)

        db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()