from flask.testing import FlaskClient

from energytt_platform.bus.messages.meteringpoints import \
    MeteringPointRemoved

from meteringpoints_consumer.handlers import dispatcher

from meteringpoints_shared.db import db

from ...helpers import \
    insert_meteringpoint_and_delegate_access_to_subject, \
    insert_technology_from_meteringpoint, \
    get_dummy_meteringpoint, \
    make_dict_of_metering_point


class TestMeteringPointRemoved:
    def test__insert_one_mp_then_remove_it__fetched_result_is_empty(
            self,
            session: db.Session,
            client: FlaskClient,
            valid_token_encoded: str,
    ):

        # -- Arrange ---------------------------------------------------------

        subject = 'bar'

        mp = get_dummy_meteringpoint(
            number=1,
            include_address=True,
            include_technology=True,
        )

        insert_technology_from_meteringpoint(
            meteringpoint=mp
        )

        insert_meteringpoint_and_delegate_access_to_subject(
            meteringpoint=mp,
            token_subject=subject,
        )

        # -- Act -------------------------------------------------------------

        dispatcher(MeteringPointRemoved(
            gsrn=mp.gsrn,
        ))

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
                'Authorization': f'Bearer: {valid_token_encoded}'
            }
        )

        # -- Assert ----------------------------------------------------------

        assert r.status_code == 200
        assert len(r.json['meteringpoints']) == 0

    def test__insert_multiple_mps_then_remove_one__correct_mp_removed(
            self,
            session: db.Session,
            client: FlaskClient,
            valid_token_encoded: str,
    ):

        # -- Arrange ---------------------------------------------------------

        subject = 'bar'

        mp_1 = get_dummy_meteringpoint(
            number=1,
            include_address=True,
            include_technology=True,
        )
        insert_technology_from_meteringpoint(meteringpoint=mp_1)
        insert_meteringpoint_and_delegate_access_to_subject(
            meteringpoint=mp_1,
            token_subject=subject,
        )

        mp_2 = get_dummy_meteringpoint(
            number=2,
            include_address=True,
            include_technology=True,
        )
        insert_technology_from_meteringpoint(meteringpoint=mp_2)
        insert_meteringpoint_and_delegate_access_to_subject(
            meteringpoint=mp_2,
            token_subject=subject,
        )

        # -- Act -------------------------------------------------------------

        dispatcher(MeteringPointRemoved(
            gsrn=mp_1.gsrn,
        ))

        r = client.post(
            path='/list',
            json={
                'offset': 0,
                'limit': 10,
                'filters': {
                    'gsrn': [mp_1.gsrn, mp_2.gsrn],
                },
            },
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}'
            }
        )

        # -- Assert ----------------------------------------------------------
        expected_result = make_dict_of_metering_point(mp_2)

        assert r.status_code == 200
        assert len(r.json['meteringpoints']) == 1

        assert r.json['meteringpoints'][0] == expected_result
