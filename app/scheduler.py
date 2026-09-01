from apscheduler.schedulers.blocking import BlockingScheduler
from .jobs import main
scheduler = BlockingScheduler(timezone="Asia/Kolkata")
scheduler.add_job(main, "cron", hour=9, minute=0)
if __name__ == "__main__":
    main(); scheduler.start()
