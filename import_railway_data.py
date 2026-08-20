import csv
from datetime import datetime

from app.database.session import sessionlocal
from app.models.silver_price import PriceModel
from app.models.sources import SourceModel


CSV_FILE = "silver_prices.csv"


def import_data():
    db = sessionlocal()

    try:
        sources = {
            source.name: source.id
            for source in db.query(SourceModel).all()
        }

        with open(
            CSV_FILE,
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as file:

            reader = csv.DictReader(file)

            for row in reader:
                source_name = row["source"]

                if source_name not in sources:
                    raise ValueError(
                        f"Unknown source: {source_name}"
                    )

                price = PriceModel(
                    source_id=sources[source_name],
                    price=row["price"],
                    currency="IRT",
                    fetched_at=datetime.fromisoformat(
                        row["fetched_at"]
                    ),
                    created_at=datetime.fromisoformat(
                        row["created_at"]
                    ),
                )

                db.add(price)

        db.commit()

        print("Data imported successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    import_data()