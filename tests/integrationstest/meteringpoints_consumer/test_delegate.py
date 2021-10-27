import pytest
from typing import Dict, Any, List
from flask.testing import FlaskClient

from energytt_platform.bus import messages as m
from energytt_platform.serialize import simple_serializer
from energytt_platform.models.delegates import MeteringPointDelegate
from energytt_platform.models.meteringpoints import \
    MeteringPointType, MeteringPoint

from meteringpoints_consumer.handlers import dispatcher
from meteringpoints_shared.db import db

# TODO: Implementering
#   - Grant access, revoke access, grant access again

METERINGPOINT_1 = MeteringPoint(
    gsrn='gsrn1',
    sector='DK1',
    type=MeteringPointType.production,
)

METERINGPOINT_2 = MeteringPoint(
    gsrn='gsrn2',
    sector='DK1',
    type=MeteringPointType.production,
)

METERINGPOINT_3 = MeteringPoint(
    gsrn='gsrn3',
    sector='DK1',
    type=MeteringPointType.production,
)

# Representation of MeteringPoints using simple Python data-types:

METERINGPOINT_1_simple = simple_serializer.serialize(METERINGPOINT_1)
METERINGPOINT_2_simple = simple_serializer.serialize(METERINGPOINT_2)
METERINGPOINT_3_simple = simple_serializer.serialize(METERINGPOINT_3)

METERINGPOINTS = [
    METERINGPOINT_1,
    METERINGPOINT_2,
    METERINGPOINT_3,
]


# TODO: Remove seedin function, no need for it
@pytest.fixture(scope='function')
def seed_meteringpoints(session: db.Session,):
    """
    Insert dummy meteringpoints into the database
    """

    for meteringpoint in METERINGPOINTS:
        dispatcher(m.MeteringPointUpdate(
            meteringpoint=meteringpoint,
        ))

# -- Tests -------------------------------------------------------------------


class TestMeteringPointDelegateGranted:
    # TODO: No need to parametrize (So remove this)
    @pytest.mark.parametrize('gsrn, expected_result', (
        (METERINGPOINT_1.gsrn, METERINGPOINT_1_simple),
        (METERINGPOINT_2.gsrn, METERINGPOINT_2_simple),
        (METERINGPOINT_3.gsrn, METERINGPOINT_3_simple),
    ))
    def test__grant_access_to_single_meteringpoint__should_return_meteringpoint(  # noqa: E501
        self,
        seed_meteringpoints,
        token_subject: str,
        client: FlaskClient,
        valid_token_encoded: str,
        gsrn: str,
        expected_result: Dict[str, Any],
    ):
        # -- Act -------------------------------------------------------------

        dispatcher(m.MeteringPointDelegateGranted(
            delegate=MeteringPointDelegate(
                subject=token_subject,
                gsrn=gsrn,
            ),
        ))

        r = client.post(
            path='/list',
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}'
            },
        )
        # -- Assert ----------------------------------------------------------
        assert r.status_code == 200
        assert r.json == {
            'success': True,
            'total': 1,
            'meteringpoints': [expected_result],
        }

    def test__do_not_grant_access_to_meteringpoint__should_not_return_meteringpoint(  # noqa: E501
        self,
        seed_meteringpoints,
        client: FlaskClient,
        valid_token_encoded: str,
    ):
        # -- Act -------------------------------------------------------------

        r = client.post(
            path='/list',
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}'
            },
        )
        # -- Assert ----------------------------------------------------------
        assert r.status_code == 200
        assert r.json == {
            'success': True,
            'total': 0,
            'meteringpoints': [],
        }


class TestMeteringPointDelegateRevoked:
    # TODO: No need for three tests, move into code
    @pytest.mark.parametrize('gsrn, expected_result', (
        (METERINGPOINT_1.gsrn, [METERINGPOINT_2_simple, METERINGPOINT_3_simple]),  # noqa: E501
        (METERINGPOINT_2.gsrn, [METERINGPOINT_1_simple, METERINGPOINT_3_simple]),  # noqa: E501
        (METERINGPOINT_3.gsrn, [METERINGPOINT_1_simple, METERINGPOINT_2_simple]),  # noqa: E501
    ))
    def test__revoke_access_to_single_meteringpoint__should_return_not_meteringpoint(  # noqa: E501
        self,
        seed_meteringpoints,
        token_subject: str,
        client: FlaskClient,
        valid_token_encoded: str,
        gsrn: str,
        expected_result: List[Dict[str, Any]],
    ):
        # -- Act -------------------------------------------------------------

        # Grant access to all
        for meteringpoint in METERINGPOINTS:
            dispatcher(m.MeteringPointDelegateGranted(
                delegate=MeteringPointDelegate(
                    subject=token_subject,
                    gsrn=meteringpoint.gsrn,
                )
            ))

        # Revoke access to single
        dispatcher(m.MeteringPointDelegateRevoked(
            delegate=MeteringPointDelegate(
                subject=token_subject,
                gsrn=gsrn,
            )
        ))

        r = client.post(
            path='/list',
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}'
            },
        )
        # -- Assert ----------------------------------------------------------
        assert r.status_code == 200
        assert r.json == {
            'success': True,
            'total': len(expected_result),
            'meteringpoints': expected_result,
        }
