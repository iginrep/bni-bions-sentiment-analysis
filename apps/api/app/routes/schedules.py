from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from pipeline.storage.schedules import list_schedules as list_schedule_docs, toggle_schedule

router = APIRouter()


def _serialize(doc: dict) -> dict:
    doc["id"] = str(doc.pop("_id"))
    return doc


class ToggleRequest(BaseModel):
    isActive: bool


@router.get("")
def list_schedules():
    # List all schedules (both active and inactive) so the dashboard can manage them
    return [_serialize(doc) for doc in list_schedule_docs(active_only=False)]


@router.put("/{schedule_id}/toggle")
def toggle_schedule_route(schedule_id: str, payload: ToggleRequest):
    success = toggle_schedule(schedule_id, payload.isActive)
    if not success:
        raise HTTPException(status_code=404, detail="Schedule not found or status unchanged")
    return {"id": schedule_id, "isActive": payload.isActive}
