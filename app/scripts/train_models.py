from app.database.session import sessionlocal
from app.prediction.training import train_models


def main():
    db = sessionlocal()

    try:
        train_models(db)

    finally:
        db.close()


if __name__ == "__main__":
    main()