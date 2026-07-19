from app.core.config import get_settings


def test_settings_are_typed_and_database_url_is_masked() -> None:
    settings = get_settings()

    assert settings.app_env == "development"
    assert settings.app_port == 8000
    assert str(settings.database_url) == "**********"
    assert "http://localhost:5173" in settings.cors_origins
