from energytt_platform.bus.messages.tech import TechnologyUpdate
from energytt_platform.models.tech import TechnologyCodes
from flask.testing import FlaskClient

from energytt_platform.bus.messages.meteringpoints import \
    MeteringPointTechnologyUpdate

from meteringpoints_consumer.handlers import dispatcher

from meteringpoints_shared.db import db

from ...helpers import \
    insert_meteringpoint_and_delegate_access_to_subject, \
    make_dict_of_metering_point, \
    insert_technology_from_meteringpoint, \
    get_dummy_meteringpoint, \
    get_dummy_technology


class TestMeteringPointTechnologyUpdate:
    def test__insert_mp_without_tech_then_add_tech__tech_inserted_correctly(
            self,
            session: db.Session,
            client: FlaskClient,
            valid_token_encoded: str,
    ):
        """
        Test Case(s):
            TEST_5 Create/Update/remove meteringpoint.technology
                TEST_5.1 Insert meteringpoint.technology

            Addtionally tests the following:
                - Correct amount of meteringpoints returned
                - HTTP status code

        Steps:
            1. Create dummy meteringpoint without technology
            2. Insert dummy point
            3. Insert new technology to meteringpoint
            3. Fetch meteringpoint using /list
            4. Assert fetched technology equals the dummy technology
        """

        # -- Arrange ---------------------------------------------------------

        subject = 'bar'

        meteringpoint = get_dummy_meteringpoint(
            number=1,
            include_address=True,
            include_technology=False,
        )

        technology = get_dummy_technology(1)

        insert_meteringpoint_and_delegate_access_to_subject(
            meteringpoint=meteringpoint,
            token_subject=subject,
        )

        dispatcher(TechnologyUpdate(
            technology=technology
        ))

        # -- Act -------------------------------------------------------------

        # Insert technology to metering point
        dispatcher(MeteringPointTechnologyUpdate(
            gsrn=meteringpoint.gsrn,
            codes=TechnologyCodes(
                tech_code=technology.tech_code,
                fuel_code=technology.fuel_code
            )
        ))

        r = client.post(
            path='/list',
            json={
                'offset': 0,
                'limit': 10,
                'filters': {
                    'gsrn': [meteringpoint.gsrn],
                },
            },
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}'
            }
        )

        # -- Assert ----------------------------------------------------------
        meteringpoint.technology = technology
        expected_result = make_dict_of_metering_point(meteringpoint)
        assert r.status_code == 200
        assert r.json['meteringpoints'][0] == expected_result

    def test__insert_mp_with_tech_then_up_tech__tech_updated_correctly(
            self,
            session: db.Session,
            client: FlaskClient,
            valid_token_encoded: str,
    ):
        """
        Test Case(s):
            TEST_5 Create/Update/remove meteringpoint.technology
                TEST_5.2 Update meteringpoint.technology

            Addtionally tests the following:
                - Correct amount of meteringpoints returned
                - HTTP status code

        Steps:
            1. Create dummy meteringpoint with technology
            2. Insert dummy point
            3. Create new technology
            4. Ypdate meteringpoint technology with new technology
            5. Fetch meteringpoint using /list
            6. Assert fetched technology equals the new dummy technology
        """

        # -- Arrange ---------------------------------------------------------

        subject = 'bar'

        mp = get_dummy_meteringpoint(
            number=1,
            include_address=True,
            include_technology=True,
        )

        technology = get_dummy_technology(2)

        dispatcher(TechnologyUpdate(
            technology=mp.technology
        ))

        dispatcher(TechnologyUpdate(
            technology=technology
        ))

        insert_meteringpoint_and_delegate_access_to_subject(
            meteringpoint=mp,
            token_subject=subject,
        )

        # -- Act -------------------------------------------------------------

        # Update metering point technology
        dispatcher(MeteringPointTechnologyUpdate(
            gsrn=mp.gsrn,
            codes=TechnologyCodes(
                tech_code=technology.tech_code,
                fuel_code=technology.fuel_code
            ),
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

        mp.technology = technology
        expected_result = make_dict_of_metering_point(mp)

        assert r.status_code == 200
        assert r.json['meteringpoints'][0] == expected_result

    def test__remove_technology_from_mp__technology_removed_correctly(
            self,
            session: db.Session,
            client: FlaskClient,
            valid_token_encoded: str,
    ):
        """
        Test Case(s):
            TEST_5 Create/Update/remove meteringpoint.technology
                TEST_5.3 Remove meteringpoint.technology

            Addtionally tests the following:
                - Correct amount of meteringpoints returned
                - HTTP status code

        Steps:
            1. Create dummy meteringpoint with technology
            2. Insert dummy point
            3. Remove meteringpoint technology
            5. Fetch meteringpoint using /list
            6. Assert fetched meteringpoint.technology equals None
        """

        # -- Arrange ---------------------------------------------------------

        subject = 'bar'

        mp = get_dummy_meteringpoint(
            number=1,
            include_address=True,
            include_technology=True,
        )

        insert_meteringpoint_and_delegate_access_to_subject(
            meteringpoint=mp,
            token_subject=subject,
        )

        insert_technology_from_meteringpoint(meteringpoint=mp)

        # -- Act -------------------------------------------------------------

        # Remove meteringpoint.technology by setting it to None
        dispatcher(MeteringPointTechnologyUpdate(
            gsrn=mp.gsrn,
            codes=None,
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
        mp.technology = None
        expected_result = make_dict_of_metering_point(mp)

        assert r.status_code == 200
        assert r.json['meteringpoints'][0] == expected_result
