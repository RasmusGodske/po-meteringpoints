import pytest
from flask.testing import FlaskClient
from typing import List, Dict, Any, Tuple, Optional

from energytt_platform.tokens import TokenEncoder

from meteringpoints_shared.db import db

from tests.helpers import get_dummy_token


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


class TestScopes:
    """
    TODO Describe me
    """

    def test__token_has_required_scope__should_return_status_200(
            self,
            endpoint: TEndpoint,
            session: db.Session,
            client: FlaskClient,
            token_encoder: TokenEncoder,
    ):

        # -- Arrange ---------------------------------------------------------

        method, path, scopes, query = endpoint

        token = get_dummy_token(
            token_encoder=token_encoder,
            subject='bar',
            actor='foo',
            expired=False,
            scopes=scopes,
        )

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
                'Authorization': f'Bearer: {token}'
            },
        )

        # -- Assert ----------------------------------------------------------

        assert r.status_code == 200

    @pytest.mark.parametrize('scopes', [
        [],
        ['something'],
    ])
    def test__token_missing_required_scope__should_return_status_401(
            self,
            endpoint: TEndpoint,
            scopes: List[str],
            session: db.Session,
            client: FlaskClient,
            token_encoder: TokenEncoder,
    ):

        # -- Arrange ---------------------------------------------------------

        method, path, _, query = endpoint

        token = get_dummy_token(
            token_encoder=token_encoder,
            subject='bar',
            actor='foo',
            expired=False,
            scopes=scopes,
        )

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
                'Authorization': f'Bearer: {token}'
            },
        )

        # -- Assert ----------------------------------------------------------

        assert r.status_code == 401
