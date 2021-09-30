from flask.testing import FlaskClient

from energytt_platform.bus.messages.meteringpoints import \
    MeteringPointAddressUpdate

from meteringpoints_consumer.handlers import dispatcher

from meteringpoints_shared.db import db

from ...helpers import \
    insert_meteringpoint_and_delegate_access_to_subject, \
    make_dict_of_metering_point, \
    insert_technology_from_meteringpoint, \
    get_dummy_meteringpoint, \
    get_dummy_address


class TestMeteringPointAddressUpdate:
    def test__add_address_to_mp__address_inserted_correctly(
            self,
            session: db.Session,
            client: FlaskClient,
            valid_token_encoded: str,
    ):
        # -- Arrange ---------------------------------------------------------

        subject = 'bar'

        mp = get_dummy_meteringpoint(
            number=1,
            include_address=False,
            include_technology=True,
        )

        address = get_dummy_address(1)

        insert_technology_from_meteringpoint(
            meteringpoint=mp
        )

        # Insert single metering point
        insert_meteringpoint_and_delegate_access_to_subject(
            meteringpoint=mp,
            token_subject=subject,
        )

        mp.address = address

        expected_result = make_dict_of_metering_point(mp)

        # -- Act -------------------------------------------------------------

        # Insert address to metering point
        dispatcher(MeteringPointAddressUpdate(
            gsrn=mp.gsrn,
            address=address,
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
        assert len(r.json['meteringpoints']) == 1

        assert r.json['meteringpoints'][0] == expected_result

    def test__update_mp_address__address_updates_correctly(
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

        # Create new address with difference values from mp.address
        address = get_dummy_address(2)

        insert_technology_from_meteringpoint(
            meteringpoint=mp
        )

        insert_meteringpoint_and_delegate_access_to_subject(
            meteringpoint=mp,
            token_subject=subject,
        )

        # -- Act -------------------------------------------------------------

        # Update metering point address to the new given address
        dispatcher(MeteringPointAddressUpdate(
            gsrn=mp.gsrn,
            address=address,
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
        mp.address = address
        expected_result = make_dict_of_metering_point(mp)

        assert r.status_code == 200
        assert len(r.json['meteringpoints']) == 1

        assert r.json['meteringpoints'][0] == expected_result

    def test__remove_mp_address__address_removed_correctly(
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

        # delete metering point address
        dispatcher(MeteringPointAddressUpdate(
            gsrn=mp.gsrn,
            address=None,
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
        mp.address = None
        expected_result = make_dict_of_metering_point(mp)
        assert r.status_code == 200
        assert r.json['meteringpoints'][0] == expected_result
