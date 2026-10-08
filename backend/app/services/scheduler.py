"""Automatic historical job data collection scheduler using APScheduler."""

import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.database import get_session_factory
from app.services.job_service import collect_and_ingest
from app.services.analysis_service import run_analysis_snapshot

logger = logging.getLogger(__name__)

_scheduler: Optional[BackgroundScheduler] = None
_last_run_time: Optional[datetime] = None
_last_run_status: str = "never_run"
_current_interval: str = "daily"  # "daily", "weekly", "manual"


def run_scheduled_pipeline():
    """Execute the full end-to-end scheduled collection pipeline:
    1. Collect jobs from configured real sources
    2. Normalize roles and locations
    3. Deduplicate against existing database records
    4. Extract skills & track emerging candidates
    5. Save analysis snapshot
    """
    global _last_run_time, _last_run_status
    _last_run_time = datetime.now(timezone.utc)
    _last_run_status = "running"
    logger.info("Executing scheduled job market collection pipeline...")

    session_factory = get_session_factory()
    with session_factory() as db:
        try:
            # 1-4: Collect and ingest
            result = collect_and_ingest(
                source="all_real",
                country="Worldwide",
                role="Software Engineer",
                max_results=50,
                db=db,
            )
            logger.info(
                f"Scheduled collection finished: retrieved={result.retrieved}, "
                f"new={result.new_jobs}, dupes={result.duplicates}, errors={result.errors}"
            )

            # 5: Trigger analysis snapshot for real data
            snapshot = run_analysis_snapshot(
                db=db,
                source="all",
                time_period="30d",
                data_type="real",
            )
            logger.info(f"Historical analysis snapshot #{snapshot.id} saved for {snapshot.jobs_analyzed} jobs.")

            _last_run_status = "completed" if result.errors == 0 else "partial"

        except Exception as e:
            _last_run_status = "failed"
            logger.error(f"Scheduled collection pipeline failed: {e}", exc_info=True)


def init_scheduler(frequency: str = "daily") -> BackgroundScheduler:
    """Initialize and start the BackgroundScheduler."""
    global _scheduler, _current_interval
    if _scheduler is not None and _scheduler.running:
        return _scheduler

    _scheduler = BackgroundScheduler(daemon=True)
    _current_interval = frequency

    # Configure interval trigger
    if frequency == "daily":
        trigger = IntervalTrigger(days=1)
    elif frequency == "weekly":
        trigger = IntervalTrigger(weeks=1)
    else:
        trigger = None  # Manual mode, no periodic trigger

    if trigger:
        _scheduler.add_job(
            run_scheduled_pipeline,
            trigger=trigger,
            id="jobpulse_collector_pipeline",
            name="JobPulse Periodic Collector",
            replace_existing=True,
        )

    _scheduler.start()
    logger.info(f"JobPulse background scheduler started (mode: {frequency}).")
    return _scheduler


def get_scheduler_status() -> Dict[str, Any]:
    """Return current scheduler operational status."""
    global _scheduler, _last_run_time, _last_run_status, _current_interval

    is_running = _scheduler is not None and _scheduler.running
    next_run = None

    if is_running and _scheduler.get_job("jobpulse_collector_pipeline"):
        job = _scheduler.get_job("jobpulse_collector_pipeline")
        if job and job.next_run_time:
            next_run = job.next_run_time.isoformat()

    return {
        "running": is_running,
        "interval": _current_interval,
        "last_run": _last_run_time.isoformat() if _last_run_time else None,
        "last_status": _last_run_status,
        "next_run": next_run,
    }


def trigger_immediate_collection():
    """Trigger an immediate pipeline execution on demand."""
    import threading
    t = threading.Thread(target=run_scheduled_pipeline, daemon=True)
    t.start()
    return {"status": "started", "message": "Collection pipeline triggered in background."}


def set_scheduler_interval(frequency: str):
    """Update scheduler frequency: 'daily', 'weekly', 'manual'."""
    global _scheduler, _current_interval
    if frequency not in ("daily", "weekly", "manual"):
        raise ValueError("Invalid frequency. Must be 'daily', 'weekly', or 'manual'.")

    _current_interval = frequency
    if _scheduler and _scheduler.running:
        if _scheduler.get_job("jobpulse_collector_pipeline"):
            _scheduler.remove_job("jobpulse_collector_pipeline")

        if frequency == "daily":
            _scheduler.add_job(
                run_scheduled_pipeline,
                trigger=IntervalTrigger(days=1),
                id="jobpulse_collector_pipeline",
                name="JobPulse Periodic Collector",
            )
        elif frequency == "weekly":
            _scheduler.add_job(
                run_scheduled_pipeline,
                trigger=IntervalTrigger(weeks=1),
                id="jobpulse_collector_pipeline",
                name="JobPulse Periodic Collector",
            )
