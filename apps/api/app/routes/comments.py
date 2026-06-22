from fastapi import APIRouter

from apps.api.app.repositories.social_items import list_social_items
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


@router.post("/{social_item_id}/actions")
def create_dashboard_action(social_item_id: str, action_type: str = "view"):
    """Log a dashboard action (view, favorite, comment, etc.)."""
    action_id = log_dashboard_action(action_type, social_item_id=social_item_id)
    return {"id": action_id, "socialItemId": social_item_id, "actionType": action_type}
