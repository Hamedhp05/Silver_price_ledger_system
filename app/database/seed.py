from sqlalchemy.orm import Session

from app.database.session import sessionlocal
from app.models.sources import SourceModel


sources = [
    SourceModel(
        name="tgju",
        type="API",
        enabled=True,
    ),
    SourceModel(
        name="silfam",
        type="Scraper",
        enabled=True,
    ),
    SourceModel(
        name="noghresea",
        type="Scraper",
        enabled=True,
    ),
]


def seed_sources():
    db: Session = sessionlocal()

    try:
        for source in sources:
            existing_source = db.query(SourceModel).filter_by(name=source.name).first()

            if existing_source is None:
                db.add(source)

        db.commit()

        return "Sources set successfully"

    finally:
        db.close()