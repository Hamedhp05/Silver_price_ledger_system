from apscheduler.schedulers.background import BackgroundScheduler

from app.collectors.price_collector import collect_prices


scheduler = BackgroundScheduler()


def start_scheduler():
    scheduler.add_job(
        collect_prices,
        "interval",
        hours=1,
        id="collect_silver_prices",
        replace_existing=True,
    )

    scheduler.start()
    print("scheduler start")


def stop_scheduler():
    scheduler.shutdown()
    print("scheduler shutdown")