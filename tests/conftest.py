"""
conftest.py according to pytest docs:
https://docs.pytest.org/en/2.7.3/plugins.html?highlight=re#conftest-py-plugins
"""
import pytest
from unittest.mock import patch
from datetime import datetime, timedelta, timezone

from energytt_platform.models.auth import InternalToken
from energytt_platform.tokens import TokenEncoder
from testcontainers.postgres import PostgresContainer

from meteringpoints_api.app import create_app
from meteringpoints_shared.db import db
from meteringpoints_shared.config import TOKEN_SECRET


@pytest.fixture(scope='function')
def session():
    """
    TODO
    """
    with PostgresContainer('postgres:13.4') as psql:
        with patch('meteringpoints_shared.db.db.uri', new=psql.get_connection_url()):

            # Apply migrations
            db.ModelBase.metadata.create_all(db.engine)

            # Create session
            with db.session_class() as session:
                yield session


@pytest.fixture(scope='module')
def client():
    """
    TODO
    """
    yield create_app().test_client


@pytest.fixture(scope='module')
def token_encoder():
    """
    TODO
    """
    return TokenEncoder(
        schema=InternalToken,
        secret=TOKEN_SECRET,
    )


@pytest.fixture(scope='function')
def token_subject() -> str:
    yield "bar"    


@pytest.fixture(scope='function')
def valid_token(
        token_encoder: TokenEncoder[InternalToken],
        token_subject: str,
):
    """
    TODO
    """
    yield InternalToken(
        issued=datetime.now(tz=timezone.utc),
        expires=datetime.now(tz=timezone.utc) + timedelta(days=1),
        actor='foo',
        subject=token_subject,
        scope=['meteringpoints.read'],
    )


@pytest.fixture(scope='function')
def valid_token_encoded(
        valid_token: InternalToken,
        token_encoder: TokenEncoder[InternalToken],
):
    """
    TODO
    """
    yield token_encoder.encode(valid_token)

