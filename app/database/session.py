import sqlalchemy 
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = sqlalchemy.create_engine(
    settings.settings.SQLALCHEMY_DATABASE_URL
)

sessionlocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)

def get_db():
    db = sessionlocal()
    try:
        yield db
    finally:
        db.close()