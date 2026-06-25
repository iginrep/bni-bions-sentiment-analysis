from fastapi import APIRouter

from apps.api.app.repositories.social_items import list_social_items
from apps.api.app.repositories.social_items_labeled import list_labeled_social_items, get_labeled_stats
from pipeline.storage.dashboard import log_dashboard_action

router = APIRouter()


def _serialize(doc: dict) -> dict:
    doc["id"] = str(doc.pop("_id"))
    return doc


@router.get("")
def list_comments(
    platform: str | None = None,
    targetEntity: str | None = None,
    sentimentLabel: str | None = None,
    limit: int = 50,
):
    filters = {
        "platform": platform,
        "targetEntity": targetEntity,
        "sentimentLabel": sentimentLabel,
    }
    return [_serialize(doc) for doc in list_social_items(filters, limit=limit)]


@router.get("/labeled")
def list_labeled_comments(
    platform: str | None = None,
    targetEntity: str | None = None,
    sentimentLabel: str | None = None,
    limit: int = 100,
):
    filters = {
        "platform": platform,
        "targetEntity": targetEntity,
        "sentimentLabel": sentimentLabel,
    }
    return [_serialize(doc) for doc in list_labeled_social_items(filters, limit=limit)]


@router.get("/labeled/stats")
def get_comments_stats():
    return get_labeled_stats()


@router.post("/{social_item_id}/actions")
def create_dashboard_action(social_item_id: str, action_type: str = "view"):
    """Log a dashboard action (view, favorite, comment, etc.)."""
    action_id = log_dashboard_action(action_type, social_item_id=social_item_id)
    return {"id": action_id, "socialItemId": social_item_id, "actionType": action_type}


@router.post("/extract")
def trigger_extraction():
    """Trigger collection (extraction) pipeline to fetch new comments/reviews."""
    from pipeline.collector.run import collect_sample
    try:
        # Run extraction
        collected, report = collect_sample(write=True, return_report=True)
        persisted_count = report.get("persisted_count", 0)
        return {"status": "success", "count": persisted_count}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/label")
def trigger_labeling():
    """Trigger sentiment labeling (using Gemini) on unanalyzed ulasan."""
    from sentiment_labeling import run_labeling
    try:
        stats = run_labeling()
        return {"status": "success", "stats": stats}
    except Exception as e:
        return {"status": "error", "message": str(e)}
