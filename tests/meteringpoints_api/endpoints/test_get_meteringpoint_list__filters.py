from typing import List
import pytest
from itertools import product
from flask.testing import FlaskClient

from energytt_platform.models.meteringpoints import MeteringPoint

from meteringpoints_shared.db import db
from energytt_platform.models.common import EnergyDirection

from meteringpoints_shared.models import DbMeteringPoint, DbMeteringPointDelegate
from ...helpers import \
    METERPING_POINT_TYPES, \
    make_dict_of_metering_point


mp_types = METERPING_POINT_TYPES
mp_sectors = ('SECTOR_1', 'SECTOR_2')

combinations = product(
    mp_types, mp_sectors
)


@pytest.fixture(scope='module')
def seed_meteringpoints() -> List[MeteringPoint]:
    """
    TODO

    :return:
    """

    mp_list = []

    for i, (mp_type, mp_sector) in enumerate(combinations, start=1):
        mp_list.append(DbMeteringPoint(
            gsrn=f'GSRN#{i}',
            type=mp_type,
            sector=mp_sector,
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


class TestGetMeteringPointListFilters:

    def test__filter_by_single_gsrn__single_point_fetched(
        self,
        client: FlaskClient,
        valid_token_encoded: str,
        seed_meteringpoints: List[MeteringPoint],
        seeded_session: db.Session,
    ):
        # -- Arrange ---------------------------------------------------------

        mp = seed_meteringpoints[0]

        # -- Act -------------------------------------------------------------

        r = client.post(
            path='/list',
            json={
                'offset': 0,
                'limit': 10,
                'filters': {
                    'gsrn': [mp.gsrn],
                },
            },
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}',
            }
        )

        # -- Assert ----------------------------------------------------------

        assert len(r.json['meteringpoints']) == 1

        assert r.json == {
            'meteringpoints': [make_dict_of_metering_point(mp)],
            'success': True,
            'total': 1
        }

    def test__filter_by_multiple_gsrn__multiple_point_fetched(
        self,
        client: FlaskClient,
        valid_token_encoded: str,
        seed_meteringpoints: List[MeteringPoint],
        seeded_session: db.Session,
    ):
        # -- Arrange ---------------------------------------------------------

        seed_meteringpoints_dict = {m.gsrn: m for m in seed_meteringpoints}

        gsrn_list = list(seed_meteringpoints_dict.keys())
        gsrn_list.extend(('foo', 'bar'))

        # -- Act -------------------------------------------------------------

        r = client.post(
            path='/list',
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}',
            },
            json={
                'offset': 0,
                'limit': 100,
                'filters': {
                    'gsrn': gsrn_list,
                },
            },
        )

        # -- Assert ----------------------------------------------------------

        assert r.status_code == 200

        for meteringpoint in r.json['meteringpoints']:
            expected = seed_meteringpoints_dict[meteringpoint["gsrn"]]
            assert meteringpoint == make_dict_of_metering_point(expected)

    def test__filter_by_type__correct_meteringpoints_fetched(
        self,
        client: FlaskClient,
        valid_token_encoded: str,
        seed_meteringpoints: List[MeteringPoint],
        seeded_session: db.Session,
    ):
        # -- Arrange ---------------------------------------------------------

        mp_type = EnergyDirection.consumption

        seed_meteringpoints_dict = {m.gsrn: m for m in seed_meteringpoints}

        expected_mp_list = [
            o for o in seed_meteringpoints
            if o.type == mp_type
        ]

        # -- Act -------------------------------------------------------------

        r = client.post(
            path='/list',
            json={
                'offset': 0,
                'limit': 100,
                'filters': {
                    'type': mp_type.value,
                },
            },
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}',
            }
        )

        # -- Assert ----------------------------------------------------------
        assert r.status_code == 200

        assert len(r.json['meteringpoints']) == len(expected_mp_list)

        for meteringpoint in r.json['meteringpoints']:
            expected = seed_meteringpoints_dict[meteringpoint["gsrn"]]
            assert meteringpoint == make_dict_of_metering_point(expected)

    def test__filter_by_single_sector__correct_meteringpoints_fetched(
        self,
        client: FlaskClient,
        valid_token_encoded: str,
        seed_meteringpoints: List[MeteringPoint],
        seeded_session: db.Session,
    ):
        # -- Arrange ---------------------------------------------------------

        seed_meteringpoints_dict = {m.gsrn: m for m in seed_meteringpoints}

        sector = seed_meteringpoints[0].sector

        # -- Act -------------------------------------------------------------

        r = client.post(
            path='/list',
            json={
                'offset': 0,
                'limit': 100,
                'filters': {
                    'sector': [sector],
                },
            },
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}',
            }
        )

        # -- Assert ----------------------------------------------------------

        assert r.status_code == 200

        for meteringpoint in r.json['meteringpoints']:
            expected = seed_meteringpoints_dict[meteringpoint["gsrn"]]
            assert meteringpoint == make_dict_of_metering_point(expected)

    def test__filter_by_multiple_sectors__correct_meteringpoints_fetched(
        self,
        client: FlaskClient,
        valid_token_encoded: str,
        seed_meteringpoints: List[MeteringPoint],
        seeded_session: db.Session,
    ):
        # -- Arrange ---------------------------------------------------------

        seed_meteringpoints_dict = {m.gsrn: m for m in seed_meteringpoints}

        sectors = [
            seed_meteringpoints[0].sector,
            seed_meteringpoints[1].sector,
        ]

        expected_mp_list = [
            o for o in seed_meteringpoints
            if o.sector in sectors
        ]

        # -- Act -------------------------------------------------------------

        r = client.post(
            path='/list',
            json={
                'offset': 0,
                'limit': 100,
                'filters': {
                    'sector': sectors,
                },
            },
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}',
            }
        )

        # -- Assert ----------------------------------------------------------
        assert len(r.json['meteringpoints']) == len(expected_mp_list)

        # Validate that the inserted metering points is also fetched
        assert r.status_code == 200

        assert len(r.json['meteringpoints']) == len(expected_mp_list)

        for meteringpoint in r.json['meteringpoints']:
            expected = seed_meteringpoints_dict[meteringpoint["gsrn"]]
            assert meteringpoint == make_dict_of_metering_point(expected)

    @pytest.mark.parametrize("gsrn", [
        [""], ["invalid-gsrn"], ['', 'invalid-gsrn']
    ])
    def test__filter_by_invalid_gsrn__no_points_fetched(
        self,
        client: FlaskClient,
        valid_token_encoded: str,
        seeded_session: db.Session,
        gsrn: str,
    ):
        # -- Arrange ---------------------------------------------------------

        # -- Act -------------------------------------------------------------

        r = client.post(
            path='/list',
            json={
                'offset': 0,
                'limit': 10,
                'filters': {
                    'gsrn': gsrn,
                },
            },
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}',
            }
        )

        # -- Assert ----------------------------------------------------------

        assert len(r.json['meteringpoints']) == 0
        assert r.json == {
            'meteringpoints': [],
            'success': True,
            'total': 0
        }

    @pytest.mark.parametrize("sector", [
        [""], ["invalid-sector"], ['', 'invalid-sector']
    ])
    def test__filter_by_invalid_sector__no_points_fetched(
        self,
        client: FlaskClient,
        valid_token_encoded: str,
        seeded_session: db.Session,
        sector: str,
    ):
        # -- Arrange ---------------------------------------------------------

        # -- Act -------------------------------------------------------------

        r = client.post(
            path='/list',
            json={
                'offset': 0,
                'limit': 10,
                'filters': {
                    'sector': sector,
                },
            },
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}',
            }
        )

        # -- Assert ----------------------------------------------------------
        assert r.status_code == 200
        assert r.json == {
            'meteringpoints': [],
            'success': True,
            'total': 0
        }

    @pytest.mark.parametrize("invalid_type", ["", "invalid-type"])
    def test__filter_by_invalid_type__no_points_fetched(
        self,
        client: FlaskClient,
        valid_token_encoded: str,
        seeded_session: db.Session,
        invalid_type: str,
    ):
        # -- Arrange ---------------------------------------------------------

        # -- Act -------------------------------------------------------------

        r = client.post(
            path='/list',
            json={
                'offset': 0,
                'limit': 10,
                'filters': {
                    'type': invalid_type,
                },
            },
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}',
            }
        )

        # -- Assert ----------------------------------------------------------
        assert r.status_code == 400
