from fastapi import APIRouter, HTTPException

from app.collectors.price_collector import collect_prices


router = APIRouter(
    prefix="/collector",
    tags=["Collector"],
)


@router.post("/run")
def run_collector():
    try:
        collect_prices()

        return {
            "message": "Price collection completed successfully."
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Price collection failed: {exc}",
        )