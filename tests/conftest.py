import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.database.models import Base


@pytest.fixture
def db_session() -> Session:
    engine = create_engine("sqlite:///:memory:")

    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        yield session

    engine.dispose()