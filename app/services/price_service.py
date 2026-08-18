from sqlalchemy.orm import Session
from app.models.silver_price import PriceModel
from app.models.sources import SourceModel


def get_latest_price(db: Session):
    return (
        db.query(
            PriceModel.price,
            SourceModel.name.label("source"),
            PriceModel.fetched_at.label("timestamp")
        )
        .join(
            SourceModel,
            PriceModel.source_id == SourceModel.id
        )
        .order_by(PriceModel.fetched_at.desc())
        .first()
    )



def get_price_history(
    db: Session,
    start_date=None,
    end_date=None,
    source=None,
    limit=None,
):
    query = db.query(PriceModel)

    if start_date:
        query = query.filter(
            PriceModel.fetched_at >= start_date
        )

    if end_date:
        query = query.filter(
            PriceModel.fetched_at <= end_date
        )

    if source:
        query = query.join(
            SourceModel,
            PriceModel.source_id == SourceModel.id
        ).filter(
            SourceModel.name == source
        )

    query = query.order_by(
        PriceModel.fetched_at.asc()
    )

    if limit:
        query = query.limit(limit)

    return query.all()


def get_chart_data(
    db: Session,
    point_count: int = 50,
):
    return (
        db.query(PriceModel)
        .join(SourceModel, PriceModel.source_id == SourceModel.id)
        .filter(SourceModel.name == "silfam")
        .order_by(PriceModel.fetched_at.desc())
        .limit(point_count)
        .all()
    )