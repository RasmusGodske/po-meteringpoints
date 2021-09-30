from flask.testing import FlaskClient

from energytt_platform.bus.messages.meteringpoints import MeteringPointUpdate

from meteringpoints_consumer.handlers import dispatcher

from meteringpoints_shared.db import db

from ...helpers import \
    insert_meteringpoint_and_delegate_access_to_subject, \
    make_dict_of_metering_point, \
    insert_technology_from_meteringpoint, \
    get_dummy_meteringpoint, \
    get_dummy_meteringpoint_list


class TestOnMeteringPointUpdate:

    def test__add_single_meteringpoint_and_fetch__fetched_result_matches(
            self,
            session: db.Session,
            client: FlaskClient,
            valid_token_encoded: str,
    ):
        """
        Test Case(s):
            TEST#1 Single point added and fetched result matches
                TEST#1.1 meteringpoint.technology matches
                TEST#1.2 meteringpoint.address matches
                TEST#1.3 meteringpoint.sector matches
                TEST#1.4 meteringpoint.type matches
                TEST#1.5 meteringpoint.sector matches

            Addtionally tests the following:
                - Correct amount of meteringpoints returned
                - HTTP status code

        Steps:
            1. Create dummy meteringpoint
            2. Insert dummy point
            3. Fetch meteringpoint using /list
            4. Assert fetched meteringpoint equals the dummy meteringpoint
        """

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

        # -- Act -------------------------------------------------------------

        insert_meteringpoint_and_delegate_access_to_subject(
            meteringpoint=mp,
            token_subject=subject,
        )

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

        assert r.json['meteringpoints'][0] == make_dict_of_metering_point(mp)

    def test__add_meteringpoint_then_update__meteringpoint_updated_correct(
            self,
            session: db.Session,
            client: FlaskClient,
            valid_token_encoded: str,
    ):
        """
        Test Case(s):
            TEST_2 Single point added then updated and fetched result matches
                TEST_2.1 meteringpoint.technology matches
                TEST_2.2 meteringpoint.address matches
                TEST_2.3 meteringpoint.sector matches
                TEST_2.4 meteringpoint.type matches
                TEST_2.5 meteringpoint.sector matches

            Addtionally tests the following:
                - Correct amount of meteringpoints returned
                - HTTP status code

        Steps:
            1. Create 1st dummy meteringpoint
            2. Create 2rd dummy meteringpoint with new values but same gsrn
            3. Insert 1st dummy point
            4. Insert/update 1st dummy meteringpoint with the 2rd meteringpoint
            5. Fetch meteringpoint using /list
            6. Assert fetched meteringpoint equals the 2rd dummy meteringpoint
        """

        # -- Arrange ---------------------------------------------------------

        subject = 'bar'

        static_gsrn = 'GSRN1'

        mp_old = get_dummy_meteringpoint(
            number=1,
            use_gsrn=static_gsrn,  # Static GSRN needed to update again
            include_address=True,
            include_technology=True,
        )

        mp_new = get_dummy_meteringpoint(
            number=2,  # Get new variant with new properties
            use_gsrn=static_gsrn,  # Static GSRN needed to update again
            include_address=True,
            include_technology=True,
        )

        expected_result = make_dict_of_metering_point(mp_new)

        insert_meteringpoint_and_delegate_access_to_subject(
            meteringpoint=mp_old,
            token_subject=subject,
        )

        insert_technology_from_meteringpoint(meteringpoint=mp_new)
        insert_technology_from_meteringpoint(meteringpoint=mp_old)

        # -- Act -------------------------------------------------------------

        dispatcher(MeteringPointUpdate(
            meteringpoint=mp_new,
        ))

        r = client.post(
            path='/list',
            json={
                'offset': 0,
                'limit': 10,
                'filters': {
                    'gsrn': [static_gsrn],
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

    def test__add_multiple_meteringpoints__all_meteringpoints_fetched(
            self,
            session: db.Session,
            client: FlaskClient,
            valid_token_encoded: str,
    ):
        """
        Test Case(s):
            TEST_3 Multiple points added and fetched result matches
                TEST_3.1 Fetched meteringpoint count matches inserted count
                TEST_3.2 Fetched meteringpoints matches inserted meteringpoint
                TEST_3.3 Received status code 200

            Addtionally tests the following:

        Steps:
            1. Create 10 dummy meteringpoints with different gsrn
            2. Insert dummy meteringpoints
            2. Delegate access for each gsrn
            3. Fetchs meteringpoints using /list
            4. Compare each dummy meteringpoint with fetched meteringpoint
        """

        # -- Arrange ---------------------------------------------------------

        subject = 'bar'

        # Create a list of dummy meteringpoints
        mp_list = get_dummy_meteringpoint_list(
            count=10,
            include_address=True,
            include_technology=True,
        )

        mp_gsrn_list = [o.gsrn for o in mp_list]

        for meteringpoint in mp_list:
            insert_technology_from_meteringpoint(
                meteringpoint=meteringpoint
            )

        # -- Act -------------------------------------------------------------

        for mp in mp_list:
            insert_meteringpoint_and_delegate_access_to_subject(
                meteringpoint=mp,
                token_subject=subject,
            )

        r = client.post(
            path='/list',
            json={
                'offset': 0,
                'limit': 10,
                'filters': {
                    'gsrn': mp_gsrn_list,
                },
            },
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}',
            }
        )

        # -- Assert ----------------------------------------------------------

        assert len(r.json['meteringpoints']) == len(mp_gsrn_list)

        # Validate that the inserted metering points is also fetched
        for mp in mp_list:
            mp_dict = make_dict_of_metering_point(mp)

            # Find fetched meteringpoint by gsrn
            needle = mp_dict['gsrn']
            haystack = r.json['meteringpoints']

            filtered = filter(lambda obj: obj['gsrn'] == needle, haystack)
            fetched_mp = next(filtered, None)

            if fetched_mp is None:
                assert False, 'One or more meteringpoints were not fetched'

            assert fetched_mp == mp_dict
