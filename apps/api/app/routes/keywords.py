from fastapi import APIRouter

from pipeline.storage.keywords import list_keywords as list_keyword_docs

router = APIRouter()


def _serialize(doc: dict) -> dict:
    doc["id"] = str(doc.pop("_id"))
    return doc


@router.get("")
def list_keywords(platform: str | None = None):
    return [_serialize(doc) for doc in list_keyword_docs(platform=platform)]
