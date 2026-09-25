import laggards
import monitor
import production_investing

app = production_investing.app


@app.on_event("startup")
def reschedule_directional_movers():
    monitor.scheduler.add_job(
        lambda: laggards.refresh(monitor),
        "interval",
        minutes=30,
        id="laggard-refresh",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    print("directional mover refresh interval: 30 minutes", flush=True)
