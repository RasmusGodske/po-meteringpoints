from typing import List
import pytest
from itertools import product
from flask.testing import FlaskClient

from energytt_platform.models.meteringpoints import MeteringPoint

from meteringpoints_shared.db import db

from meteringpoints_shared.models import \
    DbMeteringPoint, DbMeteringPointDelegate
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


class TestGetMeteringPointListLimit:
    @pytest.mark.parametrize("limit", [1, 2, 3, 4])
    def test__fetch_all_limit_by_x__result_limited_by_x(
        self,
        client: FlaskClient,
        valid_token_encoded: str,
        seed_meteringpoints: List[MeteringPoint],
        seeded_session: db.Session,
        limit: int,
    ):
        # -- Arrange ---------------------------------------------------------
        seed_meteringpoints_dict = {
            m.gsrn: m for m in seed_meteringpoints[0: limit]
        }
        gsrn_list = list(seed_meteringpoints_dict.keys())

        # -- Act -------------------------------------------------------------

        r = client.post(
            path='/list',
            json={
                'offset': 0,
                'limit': limit,
                'filters': {
                    'gsrn': gsrn_list,
                },
                'ordering': {
                    'order': 'asc',
                    'key': 'gsrn',
                },
            },
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}',
            }
        )

        # -- Assert ----------------------------------------------------------

        assert len(r.json['meteringpoints']) == limit

        # Validate that the inserted metering points is also fetched
        for meteringpoint in r.json['meteringpoints']:
            expected = seed_meteringpoints_dict[meteringpoint["gsrn"]]
            assert meteringpoint == make_dict_of_metering_point(expected)

    @pytest.mark.parametrize("limit", [-1, "invalid-limit", 1.5, True])
    def test__fetch_using_invalid_limit__expect_error(
        self,
        client: FlaskClient,
        valid_token_encoded: str,
        seed_meteringpoints: List[MeteringPoint],
        seeded_session: db.Session,
        limit: int,
    ):
        # -- Arrange ---------------------------------------------------------
        seed_meteringpoints_dict = {
            m.gsrn: m for m in seed_meteringpoints
        }
        gsrn_list = list(seed_meteringpoints_dict.keys())

        # -- Act -------------------------------------------------------------

        r = client.post(
            path='/list',
            json={
                'offset': 0,
                'limit': limit,
                'filters': {
                    'gsrn': gsrn_list,
                },
                'ordering': {
                    'order': 'asc',
                    'key': 'gsrn',
                },
            },
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}',
            }
        )

        # -- Assert ----------------------------------------------------------

        assert r.status_code == 400

    def test__fetch_without_limit__expect_400(
        self,
        client: FlaskClient,
        valid_token_encoded: str,
        seed_meteringpoints: List[MeteringPoint],
        seeded_session: db.Session,
    ):
        # -- Arrange ---------------------------------------------------------
        seed_meteringpoints_dict = {
            m.gsrn: m for m in seed_meteringpoints
        }
        gsrn_list = list(seed_meteringpoints_dict.keys())

        # -- Act -------------------------------------------------------------

        r = client.post(
            path='/list',
            json={
                'offset': 0,
                'filters': {
                    'gsrn': gsrn_list,
                },
                'ordering': {
                    'order': 'asc',
                    'key': 'gsrn',
                },
            },
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}',
            }
        )

        # -- Assert ----------------------------------------------------------

        assert r.status_code == 400
