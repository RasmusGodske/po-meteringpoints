import pytest
from flask.testing import FlaskClient
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Tuple, Optional

from energytt_platform.tokens import TokenEncoder
from energytt_platform.models.auth import InternalToken

from meteringpoints_shared.db import db


TEndpoint = Tuple[str, str, List[str], Optional[Dict[str, Any]]]


@pytest.fixture(params=[
    ('POST', '/list', ['meteringpoints.read'], None),
    ('GET', '/details', ['meteringpoints.read'], {'gsrn': '12345'}),
])
def endpoint(request) -> TEndpoint:
    """
    Returns (method, path, required scopes, query string)
    """
    return request.param


class TestTokens:
    """
    TODO Describe me
    """

    def test__no_authorization_header_provided__should_return_status_401(
            self,
            endpoint: TEndpoint,
            session: db.Session,
            client: FlaskClient,
            token_encoder: TokenEncoder,
    ):

        # -- Arrange ---------------------------------------------------------

        method, path, _, query = endpoint

        if method == 'GET':
            func = client.get
        elif method == 'POST':
            func = client.post
        else:
            raise RuntimeError('Should not have happened!')

        # -- Act -------------------------------------------------------------

        r = func(
            path=path,
            query_string=query,
        )

        # -- Assert ----------------------------------------------------------

        assert r.status_code == 401

    @pytest.mark.parametrize('token', ['', 'This is an invalid token'])
    def test__invalid_token_provided__should_return_status_401(
            self,
            token: str,
            endpoint: TEndpoint,
            session: db.Session,
            client: FlaskClient,
            token_encoder: TokenEncoder,
    ):

        # -- Arrange ---------------------------------------------------------

        method, path, _, query = endpoint

        # -- Act -------------------------------------------------------------

        if method == 'GET':
            func = client.get
        elif method == 'POST':
            func = client.post
        else:
            raise RuntimeError('Should not have happened!')

        r = func(
            path=path,
            query_string=query,
            headers={
                'Authorization': f'Bearer: {token}',
            },
        )

        # -- Assert ----------------------------------------------------------

        assert r.status_code == 401

    @pytest.mark.parametrize('issued, expires', [
        (
            # Token is expired
            datetime.now(tz=timezone.utc) - timedelta(days=2),
            datetime.now(tz=timezone.utc) - timedelta(days=1),
        ),
        (
            # Token is issued AFTER now
            datetime.now(tz=timezone.utc) + timedelta(days=1),
            datetime.now(tz=timezone.utc) + timedelta(days=2),
        ),
    ])
    def test__token_dates_is_invalid__should_return_status_401(
            self,
            issued: datetime,
            expires: datetime,
            endpoint: TEndpoint,
            session: db.Session,
            client: FlaskClient,
            token_encoder: TokenEncoder,
    ):

        # -- Arrange ---------------------------------------------------------

        method, path, scopes, query = endpoint

        token = token_encoder.encode(InternalToken(
            issued=issued,
            expires=expires,
            subject='bar',
            actor='foo',
            scope=scopes,
        ))

        if method == 'GET':
            func = client.get
        elif method == 'POST':
            func = client.post
        else:
            raise RuntimeError('Should not have happened!')

        # -- Act -------------------------------------------------------------

        r = func(
            path=path,
            query_string=query,
            headers={
                'Authorization': f'Bearer: {token}',
            },
        )

        # -- Assert ----------------------------------------------------------

        assert r.status_code == 401

    def test__token_is_valid__should_return_status_200(
            self,
            endpoint: TEndpoint,
            session: db.Session,
            client: FlaskClient,
            token_encoder: TokenEncoder,
    ):

        # -- Arrange ---------------------------------------------------------

        method, path, scopes, query = endpoint

        token = token_encoder.encode(InternalToken(
            issued=datetime.now(tz=timezone.utc) - timedelta(days=1),
            expires=datetime.now(tz=timezone.utc) + timedelta(days=1),
            subject='bar',
            actor='foo',
            scope=scopes,
        ))

        if method == 'GET':
            func = client.get
        elif method == 'POST':
            func = client.post
        else:
            raise RuntimeError('Should not have happened!')

        # -- Act -------------------------------------------------------------

        r = func(
            path=path,
            query_string=query,
            headers={
                'Authorization': f'Bearer: {token}',
            },
        )

        # -- Assert ----------------------------------------------------------

        assert r.status_code == 200
