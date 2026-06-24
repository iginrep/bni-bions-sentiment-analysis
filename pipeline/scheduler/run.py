from __future__ import annotations
from apscheduler.schedulers.blocking import BlockingScheduler
from pipeline.scheduler.jobs import collect_and_analyze


def main():
    scheduler = BlockingScheduler(timezone="Asia/Jakarta")
    try:
        from pipeline.storage.schedules import list_schedules

        schedules = list_schedules(active_only=True)
    except Exception:
        schedules = []

    if schedules:
        for schedule in schedules:
            cron = schedule.get("cron") or {}
            scheduler.add_job(
                collect_and_analyze,
                "cron",
                id=str(schedule.get("_id")),
                args=[str(schedule.get("_id"))],
                hour=cron.get("hour", "8,18"),
                minute=cron.get("minute", 0),
            )
    else:
        scheduler.add_job(
            collect_and_analyze,
            "cron",
            id="sched_bions_daily_10am",
            args=["sched_bions_daily_10am"],
            hour=10,
            minute=0
        )
    scheduler.start()


if __name__ == "__main__":
    main()
