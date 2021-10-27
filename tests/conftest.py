"""
conftest.py according to pytest docs:
https://docs.pytest.org/en/2.7.3/plugins.html?highlight=re#conftest-py-plugins
"""
import pytest
from unittest.mock import patch
from flask.testing import FlaskClient
from datetime import datetime, timedelta, timezone
from testcontainers.postgres import PostgresContainer

from energytt_platform.tokens import TokenEncoder
from energytt_platform.models.auth import InternalToken

from meteringpoints_api.app import create_app
from meteringpoints_shared.db import db
from meteringpoints_shared.config import INTERNAL_TOKEN_SECRET


@pytest.fixture(scope='function')
def session():
    """
    TODO
    """
    with PostgresContainer('postgres:13.4') as psql:
        with patch('meteringpoints_shared.db.db.uri', new=psql.get_connection_url()):  # noqa: E501

            # Apply migrations
            db.ModelBase.metadata.create_all(db.engine)

            # Create session
            with db.session_class() as session:
                yield session


@pytest.fixture(scope='module')
def client() -> FlaskClient:
    """
    TODO
    """
    yield create_app().test_client


@pytest.fixture(scope='module')
def token_encoder() -> TokenEncoder[InternalToken]:
    """
    Returns InternalToken encoder with correct secret embedded.
    """
    return TokenEncoder(
        schema=InternalToken,
        secret=INTERNAL_TOKEN_SECRET,
    )


@pytest.fixture(scope='function')
def token_subject() -> str:
    yield 'bar'


@pytest.fixture(scope='function')
def valid_token(
        token_encoder: TokenEncoder[InternalToken],
        token_subject: str,
) -> InternalToken:
    """
    TODO
    """
    return InternalToken(
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
) -> str:
    """
    TODO
    """
    yield token_encoder.encode(valid_token)
