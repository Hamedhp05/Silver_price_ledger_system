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

    results = []

    try:
        for source_name, scraper in SCRAPERS.items():

            try:
                source = db.query(SourceModel).filter_by(name=source_name,enabled=True).first()

                if source is None:
                    results.append({
                        "source": source_name,
                        "status": "skipped",
                        "message": (
                            "Source is disabled or not found.")
                    })
                    continue

                raw_data = scraper()
                data = normalize_price_data(raw_data)

                existing_price = db.query(PriceModel).filter(PriceModel.source_id == source.id,PriceModel.fetched_at== data["fetched_at"],).first()

                if existing_price is not None:
                    results.append({
                        "source": source_name,
                        "status": "skipped",
                        "message": "Duplicate price data.",
                    })
                    continue

                price = PriceModel(
                    source_id=source.id,
                    price=data["price"],
                    fetched_at=data["fetched_at"],
                )

                db.add(price)
                db.commit()

                results.append({
                    "source": source_name,
                    "status": "success",
                })

            except Exception as exc:
                db.rollback()

                results.append({
                    "source": source_name,
                    "status": "failed",
                    "message": str(exc),
                })

        return results

    finally:
        db.close()