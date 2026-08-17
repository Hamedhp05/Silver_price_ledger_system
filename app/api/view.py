from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import session
from app.database.session import get_db
from app.models.sources import SourceModel
from app.models.silver_price import PriceModel
from app.scrapers.noghresea import get_silver_price as noghresea_price
from app.scrapers.tgju import get_silver_price as tgju_price
from app.scrapers.silfam import get_silver_price as silfam_price
from app.collectors.normalization import normalize_price_data


router = APIRouter()


@router.get("/view_all")
def user_view_info(db : session = Depends(get_db)):
    return db.query(SourceModel).all()


@router.get("/noghresea_view")
def noghresea_view():
    return normalize_price_data(noghresea_price()),normalize_price_data(tgju_price()),normalize_price_data(silfam_price())


@router.get("/view_all_prices")
def all_prices(db : session = Depends(get_db)):
    return db.query(PriceModel).all()

@router.get("/view_prices/{source_id}")
def price_with_id(source_id : int , db : session = Depends(get_db)):
    return db.query(PriceModel).filter_by(source_id=source_id).all()


