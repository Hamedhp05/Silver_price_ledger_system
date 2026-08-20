# Silver Price Ledger System

Backend system for collecting, storing, querying, and predicting silver prices from multiple online sources.

This project is an internship backend project implemented with FastAPI, PostgreSQL, SQLAlchemy, APScheduler, web scraping, and machine learning.

## 1. Technology Stack

- Python 3.12+
- FastAPI
- PostgreSQL 15
- SQLAlchemy
- Alembic
- APScheduler
- Requests
- BeautifulSoup4
- Pandas
- Scikit-learn
- Pytest
- Docker / Docker Compose
- Swagger UI

## 2. Data Sources

The current sources are:

| Name | Type |
|---|---|
| `tgju` | API |
| `silfam` | Scraper |
| `noghresea` | Scraper |

Source names are stored in lowercase.

## 3. Project Structure

```text
silver-price-ledger/
│
├── app/
│   ├── api/
│   ├── collectors/
│   ├── config/
│   ├── database/
│   ├── models/
│   ├── prediction/
│   ├── scheduler/
│   ├── schemas/
│   ├── services/
│   ├── scraper/
│   ├── alembic/
│   └── main.py
│
├── tests/
├── Dockerfile
├── docker-compose.yml
├── docker-compose.test.yml
├── alembic.ini
├── train_models.py
├── requirements.txt
├── .env.development
├── .env.test
├── .env.production
├── .dockerignore
├── .gitignore
└── README.md
```

## 4. Prerequisites

For the normal Docker-based run:

- Docker Desktop
- Git

Local PostgreSQL is not required.

## 5. Run from GitHub

Clone the repository:

```bash
git clone <REPOSITORY_URL>
cd silver-price-ledger
```

Make sure Docker Desktop is running.

Check Docker:

```bash
docker --version
docker compose version
```

## 6. Development Environment

The development database uses:

```text
Host: localhost
Port: 5433
Database: silver_ledger
User: silver_user
Password: silver_pass
```

`.env.development` should contain:

```env
POSTGRES_USER=silver_user
POSTGRES_PASSWORD=silver_pass
POSTGRES_DB=silver_ledger
SQLALCHEMY_DATABASE_URL=postgresql+psycopg2://silver_user:silver_pass@localhost:5433/silver_ledger
```

The FastAPI container does not use `localhost` to reach PostgreSQL. Inside Docker it connects to:

```text
postgres:5432
```

The Docker Compose file supplies that internal connection.

## 7. Start the Application

From the project root:

```bash
docker compose up --build
```

Or detached:

```bash
docker compose up -d --build
```

The application starts these services:

```text
PostgreSQL
FastAPI
```

The application automatically runs:

```bash
alembic upgrade head
```

before starting Uvicorn.

## 8. Swagger and API Documentation

Open:

```text
http://localhost:8000/docs
```

ReDoc:

```text
http://localhost:8000/redoc
```

## 9. Main Endpoints

### Latest Price

```http
GET /prices/latest
```

Returns the latest available price.

### Historical Prices

```http
GET /prices/history
```

Available query parameters:

- `start_date`
- `end_date`
- `source`
- `limit`

Example:

```text
/prices/history?source=silfam&limit=20
```

### Chart Data

```http
GET /prices/chart
```

Returns chart-ready data for the latest Silfam price points.

Example:

```text
/prices/chart?point_count=50
```

The backend returns the data needed by a client to draw a chart. No frontend application is included in this project.

### Prediction

```http
GET /prediction
```

Returns the predicted price using the saved machine-learning model.

The project currently contains:

- Linear Regression
- Random Forest Regressor

### Manual Collection

```http
POST /collector/run
```

Triggers price collection manually. This is mainly intended for testing.

## 10. Automatic Collection

The Scheduler starts automatically with FastAPI.

The normal collection interval is:

```text
1 hour
```

Collection flow:

```text
Scheduler
   ↓
Collector
   ↓
Scrapers / APIs
   ↓
Normalization
   ↓
PostgreSQL
```

Temporary failure of one source should not stop collection from the other sources.

## 11. Database

The project uses three main tables:

### `sources`

| Column | Type |
|---|---|
| id | Integer |
| name | String |
| type | API / Scraper |
| enabled | Boolean |

### `silver_prices`

| Column | Type |
|---|---|
| id | Integer |
| source_id | Integer |
| price | Numeric |
| currency | String |
| fetched_at | Timestamp |
| created_at | Timestamp |

### `predictions`

| Column | Type |
|---|---|
| id | Integer |
| predicted_price | Numeric |
| model | String |
| predicted_at | Timestamp |

Historical price records are not overwritten.

## 12. Data Normalization

The normalization module handles:

- price normalization
- Persian digits
- Persian month names
- Persian/Gregorian datetime conversion
- TGJU Rial-to-Toman conversion
- validation of invalid or missing values

## 13. Machine Learning

The training module is located at:

```text
app/prediction/training.py
```

The project currently trains:

```text
Linear Regression
Random Forest Regressor
```

Initial training can be run with:

```bash
python train_models.py
```

Trained model files are stored under:

```text
app/prediction/models/
```

The prediction service loads saved models instead of retraining them on every API request.

## 14. Test Environment

The test environment uses a separate PostgreSQL database.

Start it with:

```bash
docker compose -f docker-compose.test.yml up -d
```

Test database:

```text
Host: localhost
Port: 5434
Database: silver_ledger_test
User: silver_user
Password: silver_password
```

`.env.test`:

```env
POSTGRES_USER=silver_user
POSTGRES_PASSWORD=silver_password
POSTGRES_DB=silver_ledger_test
TEST_DATABASE_URL=postgresql://silver_user:silver_password@localhost:5434/silver_ledger_test
```

Run tests:

```bash
pytest
```

The test database is separate from the development database.

## 15. Docker Database Persistence

Development PostgreSQL data is stored in the Docker volume:

```text
silver_postgres_data
```

Running:

```bash
docker compose down
```

does not remove this volume.

Do not use:

```bash
docker compose down -v
```

unless you intentionally want to delete the development database data.

A new machine that clones the GitHub repository will not automatically receive the current local database contents. Docker creates a new PostgreSQL volume on that machine.

## 16. Sharing the Existing Historical Dataset

If the project manager must start with the same historical data currently stored on the developer machine, the Docker volume itself is not a GitHub artifact.

For reproducibility, include a database export or CSV snapshot in the repository, for example:

```text
data/
└── silver_prices.csv
```

and an import script such as:

```text
scripts/
└── import_csv.py
```

The import script can be run after the containers and migrations are ready.

This is optional for simply running the application, because the application can collect new records automatically, but it is recommended when the existing historical dataset is required for immediate prediction or demonstration.

## 17. Database Migrations

Alembic configuration:

```text
alembic.ini
```

Migration directory:

```text
app/alembic/
```

Apply migrations manually:

```bash
alembic upgrade head
```

Create a new migration:

```bash
alembic revision --autogenerate -m "migration message"
```

When the application container starts, migrations are applied automatically.

## 18. Useful Docker Commands

Check containers:

```bash
docker compose ps
```

View application logs:

```bash
docker compose logs app
```

View PostgreSQL logs:

```bash
docker compose logs postgres
```

Stop the application:

```bash
docker compose down
```

Start again:

```bash
docker compose up -d
```

Rebuild:

```bash
docker compose up --build
```

## 19. Troubleshooting

### Docker is unavailable

Make sure Docker Desktop is running.

### FastAPI container exits

Check:

```bash
docker compose logs app
```

Common causes:

- PostgreSQL is not healthy
- database URL is incorrect
- Alembic migration failed
- required environment variables are missing

### Swagger does not open

Check:

```bash
docker compose ps
```

Then open:

```text
http://localhost:8000/docs
```

### Test database connection fails

Start the test PostgreSQL container:

```bash
docker compose -f docker-compose.test.yml up -d
```

Then run:

```bash
pytest
```

## 20. Testing Status

The project includes automated tests using Pytest.

The tests use the separate PostgreSQL test database on port `5434`.

## 21. Project Deliverables

- Complete backend source code
- PostgreSQL database schema
- REST API implementation
- Scheduled data collection
- Web scrapers
- Data normalization
- Machine-learning prediction module
- Swagger API documentation
- Automated tests
- Docker configuration
- UML diagrams
- Installation documentation

## 22. Acceptance Criteria

The project is considered complete when:

1. The scheduler collects prices every hour.
2. Prices are stored in PostgreSQL.
3. APIs return valid JSON.
4. Historical data can be queried.
5. Chart API returns configurable data points.
6. Prediction endpoint returns a future price estimate.
7. Swagger documentation is available.
8. The source code is modular and documented.
9. UML diagrams are provided.
10. The application runs successfully using the documented setup.

## 23. Educational Purpose

This project is an educational internship assignment.

The prediction module is for demonstration and learning purposes and should not be considered a financial forecasting system.
