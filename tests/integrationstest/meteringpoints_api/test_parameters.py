from typing import List, Any
import pytest
from itertools import product
from flask.testing import FlaskClient

from energytt_platform.models.meteringpoints import MeteringPoint

from meteringpoints_shared.db import db
from energytt_platform.models.meteringpoints import MeteringPointType

from meteringpoints_shared.models import (
    DbMeteringPoint,
    DbMeteringPointDelegate,
)


TYPES = (MeteringPointType.consumption, MeteringPointType.production)
SECTORS = ('DK1', 'DK2')
COMBINATIONS = list(product(TYPES, SECTORS))


@pytest.fixture(scope='module')
def seed_meteringpoints() -> List[MeteringPoint]:
    """
    TODO

    :return:
    """

    mp_list = []

    for i, (type, sector) in enumerate(COMBINATIONS):
        mp_list.append(DbMeteringPoint(
            gsrn=f'gsrn{i}',
            type=type,
            sector=sector,
        ))

    return mp_list


@pytest.fixture(scope='function')
def seeded_session(
        session: db.Session,
        seed_meteringpoints: List[MeteringPoint],
        token_subject: str,
) -> db.Session:
    """
    TODO

    :param session:
    :param seed_meteringpoints:
    :param token_subject:
    :return:
    """
    session.begin()

    for meteringpoint in seed_meteringpoints:
        session.add(DbMeteringPoint(
            gsrn=meteringpoint.gsrn,
            type=meteringpoint.type,
            sector=meteringpoint.sector,
        ))

        session.add(DbMeteringPointDelegate(
            gsrn=meteringpoint.gsrn,
            subject=token_subject,
        ))

    session.commit()

    yield session


class TestGetMeteringPointList:

    # -- Filter by GSRN ------------------------------------------------------

    @pytest.mark.parametrize('gsrn', [
        ['gsrn1'],
        ['gsrn2'],
        ['gsrn1', 'gsrn2'],
        ['gsrn2', 'gsrn3'],
    ])
    def test__filter_by_known_gsrn__should_return_correct_meteringpoints(
        self,
        gsrn: List[str],
        client: FlaskClient,
        valid_token_encoded: str,
        seeded_session: db.Session,
    ):

        # -- Act -------------------------------------------------------------

        r = client.post(
            path='/list',
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}',
            },
            json={
                'filters': {
                    'gsrn': gsrn,
                },
            },
        )

        # -- Assert ----------------------------------------------------------

        # Assert response JSON
        assert r.status_code == 200
        assert r.json['success'] is True
        assert r.json['total'] == len(gsrn)

        # Assert returned MeteringPoints
        returned_gsrn = [m['gsrn'] for m in r.json['meteringpoints']]

        assert len(r.json['meteringpoints']) == len(gsrn)
        assert all(g in returned_gsrn for g in gsrn)

    @pytest.mark.parametrize('gsrn', [
        ['Foo'],
        ['Bar'],
        ['Foo', 'Bar'],
    ])
    def test__filter_by_unknown_gsrn__should_return_no_meteringpoints(
        self,
        gsrn: List[str],
        client: FlaskClient,
        valid_token_encoded: str,
        seeded_session: db.Session,
    ):

        # -- Act -------------------------------------------------------------

        r = client.post(
            path='/list',
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}',
            },
            json={
                'filters': {
                    'gsrn': gsrn,
                },
            },
        )

        # -- Assert ----------------------------------------------------------

        assert r.status_code == 200
        assert r.json == {
            'success': True,
            'total': 0,
            'meteringpoints': [],
        }

    # -- Filter by Type ------------------------------------------------------

    @pytest.mark.parametrize('type', (
            MeteringPointType.consumption,
            MeteringPointType.production,
    ))
    def test__filter_by_valid_type__should_return_correct_meteringpoints(
        self,
        type: MeteringPointType,
        client: FlaskClient,
        valid_token_encoded: str,
        seeded_session: db.Session,
    ):

        # -- Act -------------------------------------------------------------

        r = client.post(
            path='/list',
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}',
            },
            json={
                'filters': {
                    'type': type.value,
                },
            },
        )

        # -- Assert ----------------------------------------------------------

        # Assert response JSON
        assert r.status_code == 200
        assert r.json['success'] is True
        assert r.json['total'] == 2

        # Assert returned MeteringPoints
        assert len(r.json['meteringpoints']) == 2
        assert all(m['type'] == type.value for m in r.json['meteringpoints'])

    @pytest.mark.parametrize('type', ('', 'Invalid type'))
    def test__filter_by_invalid_type__should_return_status_400(
        self,
        type: str,
        client: FlaskClient,
        valid_token_encoded: str,
        seeded_session: db.Session,
    ):

        # -- Act -------------------------------------------------------------

        r = client.post(
            path='/list',
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}',
            },
            json={
                'filters': {
                    'type': type,
                },
            },
        )

        # -- Assert ----------------------------------------------------------

        assert r.status_code == 400

    # -- Filter by Sector ----------------------------------------------------

    @pytest.mark.parametrize('sectors, expected_num_results', (
            (['DK1'], 2),
            (['DK2'], 2),
            (['DK1', 'DK2'], 4),
    ))
    def test__filter_by_known_sectors__should_return_correct_meteringpoints(
        self,
        sectors: List[str],
        expected_num_results: int,
        client: FlaskClient,
        valid_token_encoded: str,
        seeded_session: db.Session,
    ):

        # -- Act -------------------------------------------------------------

        r = client.post(
            path='/list',
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}',
            },
            json={
                'filters': {
                    'sector': sectors,
                },
            },
        )

        # -- Assert ----------------------------------------------------------

        # Assert response JSON
        assert r.status_code == 200
        assert r.json['success'] is True
        assert r.json['total'] == expected_num_results

        # Assert returned MeteringPoints
        assert len(r.json['meteringpoints']) == expected_num_results
        assert all(m['sector'] in sectors for m in r.json['meteringpoints'])

    @pytest.mark.parametrize('sectors', [
        ['Foo'],
        ['Bar'],
        ['Foo', 'Bar'],
    ])
    def test__filter_by_unknown_sectors__should_return_no_meteringpoints(
        self,
        sectors: List[str],
        client: FlaskClient,
        valid_token_encoded: str,
        seeded_session: db.Session,
    ):

        # -- Act -------------------------------------------------------------

        r = client.post(
            path='/list',
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}',
            },
            json={
                'filters': {
                    'sector': sectors,
                },
            },
        )

        # -- Assert ----------------------------------------------------------

        assert r.status_code == 200
        assert r.json == {
            'success': True,
            'total': 0,
            'meteringpoints': [],
        }

    # -- Offset --------------------------------------------------------------

    @pytest.mark.parametrize('offset', (-1, 1.5, 'FooBar'))
    def test__provide_invalid_offset__should_return_status_400(
        self,
        offset: Any,
        client: FlaskClient,
        valid_token_encoded: str,
        seeded_session: db.Session,
    ):

        # -- Act -------------------------------------------------------------

        r = client.post(
            path='/list',
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}',
            },
            json={
                'offset': offset,
            },
        )

        # -- Assert ----------------------------------------------------------

        assert r.status_code == 400

    def test__provide_no_offset__should_return_all_meteringpoints(
        self,
        client: FlaskClient,
        valid_token_encoded: str,
        seeded_session: db.Session,
    ):

        # -- Act -------------------------------------------------------------

        r = client.post(
            path='/list',
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}',
            },
        )

        # -- Assert ----------------------------------------------------------

        assert r.status_code == 200
        assert len(r.json['meteringpoints']) == len(COMBINATIONS)

    @pytest.mark.parametrize('offset, expected_num_results', (
            (0, 4),
            (1, 3),
            (2, 2),
            (9999, 0),
    ))
    def test__provide_valid_offset__should_return_correct_number_of_meteringpoints(  # noqa: E501
        self,
        offset: Any,
        expected_num_results: int,
        client: FlaskClient,
        valid_token_encoded: str,
        seeded_session: db.Session,
    ):

        # -- Act -------------------------------------------------------------

        r = client.post(
            path='/list',
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}',
            },
            json={
                'offset': offset,
            },
        )

        # -- Assert ----------------------------------------------------------

        assert r.status_code == 200
        assert len(r.json['meteringpoints']) == expected_num_results

    # -- Limit ---------------------------------------------------------------

    @pytest.mark.parametrize('limit', (-1, 0, 1.5, 101, 'FooBar'))
    def test__provide_invalid_limit__should_return_status_400(
        self,
        limit: Any,
        client: FlaskClient,
        valid_token_encoded: str,
        seeded_session: db.Session,
    ):

        # -- Act -------------------------------------------------------------

        r = client.post(
            path='/list',
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}',
            },
            json={
                'limit': limit,
            },
        )

        # -- Assert ----------------------------------------------------------

        assert r.status_code == 400

    def test__provide_no_limit__should_use_default_limit(
        self,
        client: FlaskClient,
        valid_token_encoded: str,
        seeded_session: db.Session,
    ):

        # -- Act -------------------------------------------------------------

        r = client.post(
            path='/list',
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}',
            },
        )

        # -- Assert ----------------------------------------------------------

        assert r.status_code == 200
        assert len(r.json['meteringpoints']) == 4

    @pytest.mark.parametrize('limit, expected_num_results', (
            (1, 1),
            (2, 2),
            (3, 3),
            (4, 4),
            (5, 4),
    ))
    def test__provide_valid_limit__should_return_correct_number_of_meteringpoints(  # noqa: E501
        self,
        limit: Any,
        expected_num_results: int,
        client: FlaskClient,
        valid_token_encoded: str,
        seeded_session: db.Session,
    ):

        # -- Act -------------------------------------------------------------

        r = client.post(
            path='/list',
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}',
            },
            json={
                'limit': limit,
            },
        )

        # -- Assert ----------------------------------------------------------

        assert r.status_code == 200
        assert len(r.json['meteringpoints']) == expected_num_results

    # -- Offset + Limit ------------------------------------------------------

    def test__provide_valid_offset_and_limit__should_return_correct_number_of_meteringpoints(  # noqa: E501
        self,
        client: FlaskClient,
        valid_token_encoded: str,
        seeded_session: db.Session,
    ):

        # -- Act -------------------------------------------------------------

        r = client.post(
            path='/list',
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}',
            },
            json={
                'offset': 1,
                'limit': 2,
            },
        )

        # -- Assert ----------------------------------------------------------

        assert r.status_code == 200
        assert len(r.json['meteringpoints']) == 2
