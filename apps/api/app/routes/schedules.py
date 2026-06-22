from fastapi import APIRouter

from pipeline.storage.schedules import list_schedules as list_schedule_docs

router = APIRouter()


def _serialize(doc: dict) -> dict:
    doc["id"] = str(doc.pop("_id"))
    return doc


@router.get("")
def list_schedules():
    return [_serialize(doc) for doc in list_schedule_docs()]
