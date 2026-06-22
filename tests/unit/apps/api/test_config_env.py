from __future__ import annotations

import os

from apps.api.app import config


def test_settings_reads_mongodb_database_env(monkeypatch):
    monkeypatch.setenv("MONGODB_URI", "mongodb://mongo:27017")
    monkeypatch.setenv("MONGODB_DATABASE", "custom_db")

    settings = config.Settings()

    assert settings.mongodb_uri == "mongodb://mongo:27017"
    assert settings.mongodb_database == "custom_db"


def test_settings_accepts_legacy_mongodb_db_env(monkeypatch):
    monkeypatch.delenv("MONGODB_DATABASE", raising=False)
    monkeypatch.setenv("MONGODB_DB", "legacy_db")

    settings = config.Settings()

    assert settings.mongodb_database == "legacy_db"
