from apscheduler.schedulers.background import BackgroundScheduler

from app.collectors.price_collector import collect_prices


scheduler = BackgroundScheduler()


def start_scheduler():
    if scheduler.running:
        return

    scheduler.add_job(
        collect_prices,
        "interval",
        hours=1,
        id="collect_silver_prices",
        replace_existing=True,
    )

    scheduler.start()

    print("Scheduler started")


def stop_scheduler():
    if not scheduler.running:
        return

    scheduler.shutdown()

    print("Scheduler stopped")