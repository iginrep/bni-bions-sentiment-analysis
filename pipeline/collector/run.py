from __future__ import annotations

from typing import Any, Iterable

from pipeline.collector.adapters.app_store import AppStoreAdapter
from pipeline.collector.adapters.google_play import GooglePlayAdapter
from pipeline.collector.adapters.instagram import InstagramAdapter
from pipeline.collector.adapters.stockbit import StockbitAdapter
from pipeline.collector.adapters.threads import ThreadsAdapter
from pipeline.collector.adapters.tiktok import TikTokResearchAdapter
from pipeline.collector.adapters.twitter import TwitterAdapter
from pipeline.collector.adapters.youtube import YouTubeAdapter
from pipeline.collector.base import CollectorAdapter, RawSocialItem
from pipeline.collector.config_validator import detect_missing_env
from pipeline.collector.dedupe import dedupe_items
from pipeline.collector.exceptions import CollectorNotConfigured, CollectorStopped

# adapter class → mongo-init.js provider _id
_PROVIDER_MAP: dict[str, str] = {
    "GooglePlayAdapter": "provider_google_play_reviews",
    "AppStoreAdapter": "provider_app_store_reviews",
    "YouTubeAdapter": "provider_youtube_comments",
    "StockbitAdapter": "provider_stockbit_playwright",
    "TwitterAdapter": "provider_x_twscrape",
    "TikTokResearchAdapter": "provider_tiktok_api",
    "InstagramAdapter": "provider_instagram_instaloader",
    "ThreadsAdapter": "provider_threads_api",
}


def remaining_platform_adapters(include_risky: bool = False) -> list[CollectorAdapter]:
    adapters: list[CollectorAdapter] = [AppStoreAdapter(), GooglePlayAdapter(), YouTubeAdapter()]
    risky_adapters: list[CollectorAdapter] = [
        StockbitAdapter(),
        TwitterAdapter(),
        TikTokResearchAdapter(),
        InstagramAdapter(),
        ThreadsAdapter(),
    ]
    if include_risky:
        adapters.extend(risky_adapters)
    return adapters


def validate_collectors(adapters: list[CollectorAdapter] | None = None) -> dict[str, dict[str, Any]]:
    active_adapters = adapters if adapters is not None else remaining_platform_adapters(include_risky=True)
    summary: dict[str, dict[str, Any]] = {}
    for adapter in active_adapters:
        platform = getattr(adapter, "platform", adapter.__class__.__name__)
        required_env = getattr(adapter, "required_env", []) or []
        missing_env = detect_missing_env(required_env) if required_env else []
        summary[platform] = {
            "required_env": required_env,
            "missing_env": missing_env,
            "configured": len(missing_env) == 0,
            "enabled_by_default": getattr(adapter, "enabled_by_default", False),
        }
    return summary


def build_report(
    items: list[RawSocialItem],
    adapters: list[CollectorAdapter] | None = None,
) -> dict[str, Any]:
    validation = validate_collectors(adapters)
    return {"validation": validation, "collected_count": len(items)}


def collect_sample(
    include_risky: bool = False,
    adapters: Iterable[CollectorAdapter] | None = None,
    return_report: bool = False,
    write: bool = False,
) -> list[RawSocialItem] | tuple[list[RawSocialItem], dict[str, dict[str, Any]]]:
    items: list[RawSocialItem] = []
    report: dict[str, dict[str, Any]] = {}
    active_adapters = list(adapters) if adapters is not None else remaining_platform_adapters(include_risky=include_risky)

    # start collection run
    run_id: str | None = None
    try:
        from pipeline.storage.collection_runs import start_run, finish_run, record_error
        from pipeline.storage.collector_providers import update_provider_health
        from pipeline.storage.system_events import log_info, log_error
        run_id = start_run(platform="multi", run_type="sample")
    except Exception:
        start_run = finish_run = record_error = update_provider_health = log_info = log_error = None  # type: ignore[assignment]

    for adapter in active_adapters:
        platform = getattr(adapter, "platform", adapter.__class__.__name__)
        adapter_class = adapter.__class__.__name__
        provider_id = _PROVIDER_MAP.get(adapter_class)
        if not getattr(adapter, "enabled_by_default", False) and not include_risky:
            report[platform] = {"status": "skipped", "count": 0}
            continue
        try:
            collected = adapter.collect(keyword="bions", target_entity="bions", limit=10)
        except CollectorNotConfigured as exc:
            report[platform] = {"status": "not_configured", "count": 0, "error": str(exc)}
            if provider_id and update_provider_health:
                try:
                    update_provider_health(provider_id, status="error", error=str(exc))
                except Exception:
                    pass
            if run_id and record_error:
                try:
                    record_error(run_id, f"{platform}: {exc}")
                except Exception:
                    pass
            continue
        except CollectorStopped as exc:
            report[platform] = {"status": "stopped", "count": 0, "error": str(exc)}
            if provider_id and update_provider_health:
                try:
                    update_provider_health(provider_id, status="error", error=str(exc))
                except Exception:
                    pass
            if run_id and record_error:
                try:
                    record_error(run_id, f"{platform}: {exc}")
                except Exception:
                    pass
            continue
        items.extend(collected)
        report[platform] = {"status": "ok", "count": len(collected)}
        if provider_id and update_provider_health:
            try:
                update_provider_health(provider_id, status="healthy")
            except Exception:
                pass

    deduped = dedupe_items(items)
    if write:
        try:
            from pipeline.storage.social_items import persist_social_items

            persist_social_items(deduped)
        except Exception:
            pass

    # finish collection run
    if run_id and finish_run:
        try:
            total_collected = sum(r.get("count", 0) for r in report.values())
            errors = [r["error"] for r in report.values() if r.get("error")]
            finish_run(
                run_id,
                status="completed" if not errors else "completed_with_errors",
                collected_count=total_collected,
                persisted_count=len(deduped) if write else 0,
                error_count=len(errors),
                errors=errors or None,
            )
        except Exception:
            pass

    if return_report:
        return deduped, report
    return deduped


if __name__ == "__main__":
    result = collect_sample(include_risky=True, return_report=True)
    items, report = result
    for item in items:
        print(item.as_json())
    if report:
        print(report)
