"""
AngelaMos | 2026
conftest.py
"""

from pathlib import Path

import pytest

from config import Settings


@pytest.fixture
def tmp_db_path(tmp_path: Path) -> Path:
    """
    Provide a temporary database path for test isolation
    """
    return tmp_path / "test_c2.db"


@pytest.fixture
def test_settings(tmp_db_path: Path) -> Settings:
    """
    Settings override pointing to a temporary database
    """
    return Settings(
        DATABASE_PATH=tmp_db_path,
        XOR_KEY="test-xor-key-12345",
        ENVIRONMENT="development",
        DEBUG=True,
    )
