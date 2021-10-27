import pytest
from typing import Dict, Any
from flask.testing import FlaskClient

from energytt_platform.bus import messages as m
from energytt_platform.serialize import simple_serializer
from energytt_platform.models.common import Address
from energytt_platform.models.delegates import MeteringPointDelegate
from energytt_platform.models.meteringpoints import \
    MeteringPointType, MeteringPoint

from meteringpoints_consumer.handlers import dispatcher
from meteringpoints_shared.db import db


# -- Test data ---------------------------------------------------------------


ADDRESS_1 = Address(
    street_code='street_code#1',
    street_name='street_name#1',
    building_number='building_number#1',
    floor_id='floor_id#1',
    room_id='room_id#1',
    post_code='post_code#1',
    city_name='city_name#1',
    city_sub_division_name='city_sub_division_name#1',
    municipality_code='municipality_code#1',
    location_description='location_description#1',
)

ADDRESS_2 = Address(
    street_code='street_code#2',
    street_name='street_name#2',
    building_number='building_number#2',
    floor_id='floor_id#2',
    room_id='room_id#2',
    post_code='post_code#2',
    city_name='city_name#2',
    city_sub_division_name='city_sub_division_name#2',
    municipality_code='municipality_code#2',
    location_description='location_description#2',
)

ADDRESS_3 = Address(
    street_code='street_code#3',
    street_name='street_name#3',
    building_number='building_number#3',
    floor_id='floor_id#3',
    room_id='room_id#3',
    post_code='post_code#3',
    city_name='city_name#3',
    city_sub_division_name='city_sub_division_name#3',
    municipality_code='municipality_code#3',
    location_description='location_description#3',
)

GSRN = 'gsrn1'

METERINGPOINT = MeteringPoint(
    gsrn=GSRN,
    sector='DK1',
    type=MeteringPointType.production,
)


METERINGPOINT_WITH_ADDRESS_1 = MeteringPoint(
    gsrn=GSRN,
    sector='DK3',
    type=MeteringPointType.production,
    address=ADDRESS_1,
)

METERINGPOINT_WITH_ADDRESS_2 = MeteringPoint(
    gsrn=GSRN,
    sector='DK3',
    type=MeteringPointType.production,
    address=ADDRESS_2,
)


# Representation of MeteringPoints using simple Python data-types:

METERINGPOINT_SIMPLE = simple_serializer.serialize(METERINGPOINT)

METERINGPOINT_WITH_ADDRESS_1_SIMPLE = \
    simple_serializer.serialize(METERINGPOINT_WITH_ADDRESS_1)

METERINGPOINT_WITH_ADDRESS_2_SIMPLE = \
    simple_serializer.serialize(METERINGPOINT_WITH_ADDRESS_2)


# -- Tests -------------------------------------------------------------------

class TestOnMeteringPointUpdate:

    # -- MeteringPointUpdate handler ----------------------------------
    @pytest.mark.parametrize('meteringpoint, updated_meteringpoint, meteringpoint_expected', (  # noqa: E501
        (
            METERINGPOINT,
            METERINGPOINT_WITH_ADDRESS_1,
            METERINGPOINT_WITH_ADDRESS_1_SIMPLE,
        ),
        (
            METERINGPOINT_WITH_ADDRESS_1,
            METERINGPOINT_WITH_ADDRESS_2,
            METERINGPOINT_WITH_ADDRESS_2_SIMPLE,
        ),
    ))
    def test__add_a_meteringpoint_without_address_then_update_the_address__should_return_updated_meteringpoint(  # noqa: E501
            self,
            session: db.Session,
            client: FlaskClient,
            valid_token_encoded: str,
            token_subject: str,
            meteringpoint: MeteringPoint,
            updated_meteringpoint: MeteringPoint,
            meteringpoint_expected: Dict[str, Any],
    ):
        """
        Adds a meteringpoint then updates it, then assert the returned
        meteringpoint matches expected result
        """

        # -- Arrange ---------------------------------------------------------

        dispatcher(m.MeteringPointDelegateGranted(
            delegate=MeteringPointDelegate(
                subject=token_subject,
                gsrn=meteringpoint.gsrn,
            ),
        ))

        # Initial MeteringPoint
        dispatcher(m.MeteringPointUpdate(
            meteringpoint=meteringpoint,
        ))

        # Updated MeteringPoint
        dispatcher(m.MeteringPointUpdate(
            meteringpoint=updated_meteringpoint,
        ))

        # -- Act -------------------------------------------------------------

        r = client.post(
            path='/list',
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}'
            },
            json={
                'filters': {
                    'gsrn': [GSRN],
                },
            },
        )

        # -- Assert ----------------------------------------------------------

        assert r.status_code == 200
        assert r.json == {
            'success': True,
            'total': 1,
            'meteringpoints': [meteringpoint_expected],
        }

    def test__add_two_meteringpoints_update_one_meteringpoint_address__should_update_correct_meteringpoints_address(  # noqa: E501
            self,
            session: db.Session,
            client: FlaskClient,
            valid_token_encoded: str,
            token_subject: str,
    ):
        """
        Adds two meteringpoints then updates it, then assert the returned
        meteringpoint matches expected result
        """
        # -- Arrange ---------------------------------------------------------
        meteringpoint_1 = MeteringPoint(
            gsrn='gsrn1',
            sector='DK1',
            type=MeteringPointType.production,
            address=ADDRESS_1,
        )

        meteringpoint_2 = MeteringPoint(
            gsrn='gsrn2',
            sector='DK1',
            type=MeteringPointType.production,
            address=ADDRESS_2,
        )

        meteringpoint_2_updated = MeteringPoint(
            gsrn='gsrn2',
            sector='DK1',
            type=MeteringPointType.production,
            address=ADDRESS_3,
        )

        meteringpoint_1_simple = \
            simple_serializer.serialize(meteringpoint_1)

        meteringpoint_2_expected_simple = \
            simple_serializer.serialize(meteringpoint_2_updated)

        meteringpoints = [
            meteringpoint_1,
            meteringpoint_2,
        ]

        # -- Act -------------------------------------------------------------

        # Insert both meteringpoints
        for meteringpoint_2 in meteringpoints:
            dispatcher(m.MeteringPointDelegateGranted(
                delegate=MeteringPointDelegate(
                    subject=token_subject,
                    gsrn=meteringpoint_2.gsrn,
                ),
            ))

            dispatcher(m.MeteringPointUpdate(
                meteringpoint=meteringpoint_2,
            ))

        # Update mertingpoint_2
        dispatcher(m.MeteringPointUpdate(
            meteringpoint=meteringpoint_2_updated
        ))

        r = client.post(
            path='/list',
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}'
            },
            json={
                'ordering': {
                    'key': 'gsrn',
                    'order': 'asc',
                }
            }
        )
        # -- Assert ----------------------------------------------------------

        assert r.status_code == 200

        assert r.json == {
            'success': True,
            'total': 2,
            'meteringpoints': [
                meteringpoint_1_simple,
                meteringpoint_2_expected_simple
            ],
        }


class TestMeteringPointAddressUpdate:
    @pytest.mark.parametrize('meteringpoint, updated_address', (  # noqa: E501
        (
            METERINGPOINT_WITH_ADDRESS_1,
            ADDRESS_2,
        ),
        (
            METERINGPOINT_WITH_ADDRESS_2,
            ADDRESS_1,
        ),
        (
            METERINGPOINT_WITH_ADDRESS_1,
            None,
        ),
        (
            METERINGPOINT,
            ADDRESS_1,
        ),
        (
            METERINGPOINT_WITH_ADDRESS_2,
            ADDRESS_2,
        ),
    ))
    def test__add_a_meteringpoint_then_update_address__should_return_updated_meteringpoint(  # noqa: E501
            self,
            session: db.Session,
            client: FlaskClient,
            valid_token_encoded: str,
            token_subject: str,
            meteringpoint: MeteringPoint,
            updated_address: Address,
    ):
        """
        Adds a meteringpoint then updates it, then assert the returned
        meteringpoint matches expected result
        """

        # -- Act -------------------------------------------------------------

        dispatcher(m.MeteringPointDelegateGranted(
            delegate=MeteringPointDelegate(
                subject=token_subject,
                gsrn=meteringpoint.gsrn,
            ),
        ))

        # Initial MeteringPoint
        dispatcher(m.MeteringPointUpdate(
            meteringpoint=meteringpoint,
        ))

        # Updated MeteringPoint
        dispatcher(m.MeteringPointAddressUpdate(
            gsrn=meteringpoint.gsrn,
            address=updated_address,
        ))

        r = client.post(
            path='/list',
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}'
            },
            json={
                'filters': {
                    'gsrn': [meteringpoint.gsrn],
                },
            },
        )

        # -- Assert ----------------------------------------------------------

        meteringpoint.address = updated_address
        expected_meteringpoint = simple_serializer.serialize(meteringpoint)

        assert r.status_code == 200
        assert r.json == {
            'success': True,
            'total': 1,
            'meteringpoints': [expected_meteringpoint],
        }

    def test__add_two_meteringpoints_update_one_meteringpoint_address__should_update_correct_meteringpoints_address(  # noqa: E501
            self,
            session: db.Session,
            client: FlaskClient,
            valid_token_encoded: str,
            token_subject: str,
    ):
        """
        Adds two meteringpoints then updates it, then assert the returned
        meteringpoint matches expected result
        """

        # -- Arrange ---------------------------------------------------------
        meteringpoint_1 = MeteringPoint(
            gsrn='gsrn1',
            sector='DK1',
            type=MeteringPointType.production,
            address=ADDRESS_1,
        )

        meteringpoint_2 = MeteringPoint(
            gsrn='gsrn2',
            sector='DK1',
            type=MeteringPointType.production,
            address=ADDRESS_2,
        )

        meteringpoint_2_updated = MeteringPoint(
            gsrn='gsrn2',
            sector='DK1',
            type=MeteringPointType.production,
            address=ADDRESS_3,
        )

        meteringpoint_1_simple = \
            simple_serializer.serialize(meteringpoint_1)

        meteringpoint_2_expected_simple = \
            simple_serializer.serialize(meteringpoint_2_updated)

        meteringpoints = [
            meteringpoint_1,
            meteringpoint_2,
        ]

        # -- Act -------------------------------------------------------------

        # Insert both meteringpoints
        for meteringpoint_2 in meteringpoints:
            dispatcher(m.MeteringPointDelegateGranted(
                delegate=MeteringPointDelegate(
                    subject=token_subject,
                    gsrn=meteringpoint_2.gsrn,
                ),
            ))

            dispatcher(m.MeteringPointUpdate(
                meteringpoint=meteringpoint_2,
            ))

        # Update mertingpoint_2
        dispatcher(m.MeteringPointAddressUpdate(
            gsrn=meteringpoint_2_updated.gsrn,
            address=meteringpoint_2_updated.address
        ))

        r = client.post(
            path='/list',
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}'
            },
            json={
                'ordering': {
                    'key': 'gsrn',
                    'order': 'asc',
                }
            }
        )
        # -- Assert ----------------------------------------------------------

        assert r.status_code == 200

        assert r.json == {
            'success': True,
            'total': 2,
            'meteringpoints': [
                meteringpoint_1_simple,
                meteringpoint_2_expected_simple
            ],
        }
