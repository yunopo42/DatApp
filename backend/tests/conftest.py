from collections.abc import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.core.config import get_settings


@pytest.fixture
def db_session() -> Generator[Session]:
    engine = create_engine(get_settings().database_url.get_secret_value())

    try:
        connection = engine.connect()
    except OperationalError:
        engine.dispose()
        pytest.skip("Local PostgreSQL is not available")

    transaction = connection.begin()
    session = Session(bind=connection, expire_on_commit=False)

    try:
        yield session
    finally:
        session.close()
        if transaction.is_active:
            transaction.rollback()
        connection.close()
        engine.dispose()
