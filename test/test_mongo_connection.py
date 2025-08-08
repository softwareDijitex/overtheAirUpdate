import pytest

from app import init_fastapi_components
from app.config import Config


def test_mongo_can_ping():
    bcrypt, mongo = init_fastapi_components()
    result = mongo.cx.admin.command("ping")
    assert result.get("ok") == 1.0, "MongoDB ping failed"


def test_db_name_present():
    assert Config.DB_NAME, "DB_NAME is not set in environment/config" 