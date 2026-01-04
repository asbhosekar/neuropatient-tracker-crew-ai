"""
Tests for configuration settings.
"""
import pytest
from src.config.settings import Settings


class TestSettings:
    """Test configuration settings."""

    def test_settings_defaults(self):
        """Test default settings values."""
        settings = Settings()

        # Check default values
        assert settings.OPENAI_MODEL == "gpt-4o-mini"
        assert settings.DATABASE_URL == "sqlite:///./neuro_tracker.db"
        assert settings.DEBUG is False
        assert settings.LOG_LEVEL == "INFO"
        assert settings.OUTPUT_DIR == "output"
        assert settings.LOGS_DIR == "logs"

    def test_settings_are_strings(self):
        """Test that key settings are strings."""
        settings = Settings()

        assert isinstance(settings.OPENAI_MODEL, str)
        assert isinstance(settings.DATABASE_URL, str)
        assert isinstance(settings.LOG_LEVEL, str)

    def test_output_directories(self):
        """Test output directory settings."""
        settings = Settings()

        assert settings.OUTPUT_DIR == "output"
        assert settings.LOGS_DIR == "logs"
