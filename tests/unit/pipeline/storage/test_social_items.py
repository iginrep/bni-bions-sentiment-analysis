from __future__ import annotations

import pytest
from pipeline.storage.social_items import to_canonical_doc

pytestmark = pytest.mark.unit


def test_to_canonical_doc_maps_snake_fields():
    doc = to_canonical_doc({
        "platform": "x",
        "source_id": "123",
        "source_type": "tweet",
        "root_source_id": "100",
        "parent_source_id": "99",
        "conversation_id": "100",
        "depth": 1,
        "relation_type": "reply",
        "keyword": "bions",
        "target_entity": "bions",
        "text": "hello",
        "author_id": "a1",
        "author_username": "testuser",
        "source_url": "https://x.com/testuser/status/123",
        "collection_method": "official_api",
        "access_risk": "low",
        "raw_payload": {"id": "123"},
    })
    assert doc["platform"] == "x"
    assert doc["sourceId"] == "123"
    assert doc["rootSourceId"] == "100"
    assert doc["parentSourceId"] == "99"
    assert doc["conversationId"] == "100"
    assert doc["depth"] == 1
    assert doc["relationType"] == "reply"
    assert doc["collectionMethod"] == "official_api"
    assert doc["accessRisk"] == "low"
    assert doc["rawPayload"] == {"id": "123"}


def test_to_canonical_doc_maps_camel_fields():
    doc = to_canonical_doc({
        "platform": "instagram",
        "sourceId": "ig1",
        "sourceType": "comment",
        "rootSourceId": "ig100",
        "depth": 2,
        "relationType": "reply",
    })
    assert doc["sourceId"] == "ig1"
    assert doc["rootSourceId"] == "ig100"
