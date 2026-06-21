from pydantic import BaseModel


class Settings(BaseModel):
    app_timezone: str = "Asia/Jakarta"
    sentiment_method: str = "rule_based"
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_database: str = "bni_bions_sentiment"


settings = Settings()
