from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database.seed import seed_sources
from app.config.logging import setup_logging
from app.api.prices import router as price_router
from app.api.collector import router as collector_router
from app.scheduler.scheduler import start_scheduler
from app.scheduler.scheduler import stop_scheduler
from app.api.prediction import router as prediction_router




@asynccontextmanager
async def lifespan(app : FastAPI):
    setup_logging()

    seed_sources()

    start_scheduler()

    yield
    
    stop_scheduler()

tags = []


tags_metadata = [
    {
        "name": "Prices",
        "description": "Operations for retrieving silver price data including latest, historical, and chart data.",
        "externalDocs": {
            "description": "More about price endpoints",
            "url": "https://example.com/docs/prices"
        }
    },
    {
        "name": "Prediction",
        "description": "AI-based price prediction using Linear Regression and Random Forest models.",
        "externalDocs": {
            "description": "More about Prediction endpoints",
            "url": "https://example.com/docs/prices"
        }
    },
    {
        "name": "Collector",
        "description": "Manual trigger for price collection from all enabled sources.",
        "externalDocs": {
            "description": "More about Collector endpoints",
            "url": "https://example.com/docs/prices"
        }
    }
]

app = FastAPI(
    lifespan=lifespan,
    openapi_tags=tags_metadata,
    title="Silver Price Ledger System",
    version="1.0.0",
    description="A backend system that periodically collects silver prices from multiple online sources, stores historical data in PostgreSQL, exposes REST APIs, and provides AI-based price predictions.",
    contact={
        "name": "Hamedhp",
        "email": "Hamedhp1384@gmail.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)

app.include_router(price_router)
app.include_router(prediction_router)
app.include_router(collector_router)
