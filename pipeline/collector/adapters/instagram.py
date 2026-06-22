from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime
from typing import Any

import httpx

from pipeline.collector.base import RawSocialItem
from pipeline.collector.exceptions import CollectorNotConfigured, CollectorStopped
from pipeline.collector.normalizer import normalize_text
from pipeline.collector.web_extract import env_csv, fetch_public_html


SHORTCODE_RE = re.compile(r"instagram\.com/(?:p|reel)/([^/?#]+)/?")
JSON_LD_RE = re.compile(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.S)
STOP_STATUSES = {401, 403, 429}
COMMENT_FIELDS = "id,text,timestamp,username,replies{id,text,timestamp,username}"
HASHTAG_MEDIA_FIELDS = "id,caption,media_type,permalink,timestamp,comments_count,like_count"


def _stable_id(prefix: str, value: str) -> str:
    return f"{prefix}_{hashlib.sha1(value.encode()).hexdigest()[:16]}"


def _shortcode(url: str) -> str:
    match = SHORTCODE_RE.search(url)
    return match.group(1) if match else _stable_id("instagram", url)


def _json_ld(html: str) -> dict[str, Any]:
    for match in JSON_LD_RE.finditer(html):
        try:
            data = json.loads(match.group(1))
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict):
            return data
    return {}


def _metric(stats: Any, name: str) -> int | None:
    if not isinstance(stats, list):
        return None
    for stat in stats:
        if name.lower() in str(stat.get("interactionType", "")).lower():
            try:
                return int(stat.get("userInteractionCount"))
            except (TypeError, ValueError):
                return None
    return None


def _parse_meta_time(value: str | None):
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _stop_on_status(response: httpx.Response, platform: str) -> None:
    if response.status_code in STOP_STATUSES:
        raise CollectorStopped(f"{platform} collector stopped: status {response.status_code}")


def parse_instagram_public_post(html: str, url: str, keyword: str, target_entity: str) -> RawSocialItem:
    data = _json_ld(html)
    source_id = str(data.get("identifier") or _shortcode(url))
    author = data.get("author") if isinstance(data.get("author"), dict) else {}
    text = normalize_text(str(data.get("articleBody") or data.get("caption") or data.get("description") or ""))
    likes = _metric(data.get("interactionStatistic"), "Like")
    metrics = {"likes": likes} if likes is not None else {}
    return RawSocialItem(
        platform="instagram",
        source_type="post",
        source_id=source_id,
        root_source_id=source_id,
        conversation_id=source_id,
        depth=0,
        keyword=keyword,
        target_entity=target_entity,
        author_username=author.get("alternateName") or author.get("name"),
        author_display_name=author.get("name"),
        text=text,
        source_url=url,
        metrics=metrics,
        raw_payload={"url": url, "json_ld": data},
        collection_method="public_http",
        access_risk="high",
    )


def _ig_comment_item(raw: dict[str, Any], media_id: str, keyword: str, target_entity: str, parent_id: str | None = None) -> RawSocialItem:
    comment_id = str(raw.get("id"))
    return RawSocialItem(
        platform="instagram",
        source_type="comment",
        source_id=comment_id,
        root_source_id=media_id,
        parent_source_id=parent_id,
        conversation_id=media_id,
        depth=2 if parent_id else 1,
        relation_type="reply" if parent_id else "comment",
        keyword=keyword,
        target_entity=target_entity,
        text=normalize_text(str(raw.get("text", ""))),
        author_username=raw.get("username"),
        posted_at=_parse_meta_time(raw.get("timestamp")),
        source_url=f"https://www.instagram.com/p/{media_id}/comments/{comment_id}",
        raw_payload=raw,
        collection_method="official_graph_api",
        access_risk="low",
    )


def parse_instagram_comments(payload: dict[str, Any], media_id: str, keyword: str, target_entity: str) -> list[RawSocialItem]:
    rows: list[RawSocialItem] = []
    for raw in payload.get("data", []):
        parent = _ig_comment_item(raw, media_id, keyword, target_entity)
        rows.append(parent)
        for reply in raw.get("replies", {}).get("data", []):
            rows.append(_ig_comment_item(reply, media_id, keyword, target_entity, parent_id=parent.source_id))
    return rows


def parse_instagram_hashtag_media(payload: dict[str, Any], query: str, keyword: str, target_entity: str) -> list[RawSocialItem]:
    rows: list[RawSocialItem] = []
    for raw in payload.get("data", []):
        source_id = str(raw.get("id"))
        rows.append(
            RawSocialItem(
                platform="instagram",
                source_type="post",
                source_id=source_id,
                root_source_id=source_id,
                conversation_id=source_id,
                depth=0,
                relation_type="mention",
                keyword=query or keyword,
                target_entity=target_entity,
                text=normalize_text(str(raw.get("caption", ""))),
                posted_at=_parse_meta_time(raw.get("timestamp")),
                source_url=raw.get("permalink"),
                metrics={"comments_count": raw.get("comments_count"), "like_count": raw.get("like_count")},
                raw_payload=raw,
                collection_method="official_instagram_hashtag_search",
                access_risk="low",
            )
        )
    return rows


class InstagramAdapter:
    platform = "instagram"
    source_type = "comment"
    access_mode = "official_graph_api"
    cost_level = "free_or_limited"
    risk_level = "low"
    enabled_by_default = False
    required_env: list[str] = ["INSTAGRAM_GRAPH_ACCESS_TOKEN"]

    def __init__(
        self,
        access_token: str | None = None,
        media_ids: list[str] | None = None,
        ig_user_id: str | None = None,
        hashtag_queries: list[str] | None = None,
        client: httpx.Client | None = None,
    ) -> None:
        self.access_token = access_token or os.getenv("INSTAGRAM_GRAPH_ACCESS_TOKEN")
        self.media_ids = media_ids if media_ids is not None else env_csv(os.getenv("INSTAGRAM_MEDIA_IDS"))
        self.ig_user_id = ig_user_id or os.getenv("INSTAGRAM_IG_USER_ID")
        self.hashtag_queries = hashtag_queries if hashtag_queries is not None else env_csv(os.getenv("INSTAGRAM_HASHTAG_QUERIES"))
        self.client = client or httpx.Client(timeout=20.0)

    def collect_media_comments(self, keyword: str, target_entity: str, limit: int = 50) -> list[RawSocialItem]:
        rows: list[RawSocialItem] = []
        for media_id in self.media_ids:
            response = self.client.get(
                f"https://graph.facebook.com/v25.0/{media_id}/comments",
                params={"fields": COMMENT_FIELDS, "access_token": self.access_token},
            )
            _stop_on_status(response, "instagram")
            response.raise_for_status()
            rows.extend(parse_instagram_comments(response.json(), media_id, keyword, target_entity))
            if len(rows) >= limit:
                break
        return rows[:limit]

    def _lookup_hashtag_id(self, query: str) -> str | None:
        response = self.client.get(
            f"https://graph.facebook.com/v25.0/{self.ig_user_id}/ig_hashtag_search",
            params={"user_id": self.ig_user_id, "q": query.lstrip("#"), "access_token": self.access_token},
        )
        _stop_on_status(response, "instagram")
        response.raise_for_status()
        data = response.json().get("data", [])
        return str(data[0].get("id")) if data else None

    def collect_hashtag_mentions(self, keyword: str, target_entity: str, limit: int = 50) -> list[RawSocialItem]:
        if self.hashtag_queries and not self.ig_user_id:
            raise CollectorNotConfigured("INSTAGRAM_IG_USER_ID missing")
        rows: list[RawSocialItem] = []
        for query in self.hashtag_queries:
            hashtag_id = self._lookup_hashtag_id(query)
            if not hashtag_id:
                continue
            media_response = self.client.get(
                f"https://graph.facebook.com/v25.0/{hashtag_id}/recent_media",
                params={"user_id": self.ig_user_id, "fields": HASHTAG_MEDIA_FIELDS, "limit": min(limit, 50), "access_token": self.access_token},
            )
            _stop_on_status(media_response, "instagram")
            media_response.raise_for_status()
            media_rows = parse_instagram_hashtag_media(media_response.json(), query, keyword, target_entity)
            rows.extend(media_rows)
            for media in media_rows:
                if len(rows) >= limit:
                    break
                comment_response = self.client.get(
                    f"https://graph.facebook.com/v25.0/{media.source_id}/comments",
                    params={"fields": COMMENT_FIELDS, "access_token": self.access_token},
                )
                _stop_on_status(comment_response, "instagram")
                comment_response.raise_for_status()
                rows.extend(parse_instagram_comments(comment_response.json(), media.source_id, query, target_entity))
            if len(rows) >= limit:
                break
        return rows[:limit]

    def collect(self, keyword: str, target_entity: str, limit: int = 50) -> list[RawSocialItem]:
        if not self.access_token:
            raise CollectorNotConfigured("INSTAGRAM_GRAPH_ACCESS_TOKEN missing")
        if not self.media_ids and not self.hashtag_queries:
            raise CollectorNotConfigured("INSTAGRAM_MEDIA_IDS or INSTAGRAM_HASHTAG_QUERIES missing")
        rows = []
        if self.media_ids:
            rows.extend(self.collect_media_comments(keyword, target_entity, limit))
        if len(rows) < limit and self.hashtag_queries:
            rows.extend(self.collect_hashtag_mentions(keyword, target_entity, limit - len(rows)))
        return rows[:limit]
