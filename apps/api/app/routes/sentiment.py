from fastapi import APIRouter
from pydantic import BaseModel
from pipeline.sentiment.classifier import classify

router = APIRouter()


class SentimentRequest(BaseModel):
    text: str
    method: str = "model"


@router.post("/classify")
def classify_text(payload: SentimentRequest):
    return classify(payload.text, method=payload.method)
