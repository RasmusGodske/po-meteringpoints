from flask.testing import FlaskClient

from meteringpoints_shared.db import db
from meteringpoints_consumer.handlers import dispatcher

from energytt_platform.tokens import TokenEncoder
from energytt_platform.bus.messages.meteringpoints import MeteringPointUpdate

from ...helpers import \
    get_dummy_token, \
    insert_meteringpoint_and_delegate_access_to_subject, \
    make_dict_of_metering_point, \
    get_dummy_meteringpoint


class TestGetMeteringPointListToken:
    def test__no_token__expect_error(
        self,
        session: db.Session,
        client: FlaskClient,
        token_encoder: TokenEncoder,
    ):
        # -- Arrange ---------------------------------------------------------

        # -- Act -------------------------------------------------------------

        r = client.post(
            path='/list',
            json={
                'offset': 0,
                'limit': 10,
                'filters': {
                    'gsrn': [],
                },
            },
            headers={
                'Authorization': 'Bearer: '
            }
        )

        # -- Assert ----------------------------------------------------------

        assert r.status_code == 401

    def test__no_authorization_header__expect_error(
        self,
        session: db.Session,
        client: FlaskClient,
        token_encoder: TokenEncoder,
    ):
        # -- Arrange ---------------------------------------------------------

        # -- Act -------------------------------------------------------------

        r = client.post(
            path='/list',
            json={
                'offset': 0,
                'limit': 10,
                'filters': {
                    'gsrn': [],
                },
            },
            headers={

            }
        )

        # -- Assert ----------------------------------------------------------

        assert r.status_code == 401

    def test__token_expired_expected_error(
        self,
        session: db.Session,
        client: FlaskClient,
        token_encoder: TokenEncoder,
    ):
        # -- Arrange ---------------------------------------------------------
        subject = 'bar'

        token = get_dummy_token(
            token_encoder=token_encoder,
            subject=subject,
            actor='foo',
            expired=True,
            scopes=['meteringpoints.read'],
        )

        mp = get_dummy_meteringpoint(
            number=1,
            include_address=False,
            include_technology=False,
        )

        insert_meteringpoint_and_delegate_access_to_subject(
            meteringpoint=mp,
            token_subject=subject,
        )

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
                'Authorization': f'Bearer: {token}'
            }
        )

        # -- Assert ----------------------------------------------------------

        assert r.status_code == 401

    def test__token_invalid_expected_error(
        self,
        session: db.Session,
        client: FlaskClient,
        token_encoder: TokenEncoder,
    ):
        # -- Arrange ---------------------------------------------------------
        subject = 'bar'

        token = 'This token can not be more invalid'

        mp = get_dummy_meteringpoint(
            number=1,
            include_address=False,
            include_technology=False,
        )

        insert_meteringpoint_and_delegate_access_to_subject(
            meteringpoint=mp,
            token_subject=subject,
        )

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
                'Authorization': f'Bearer: {token}'
            }
        )

        # -- Assert ----------------------------------------------------------

        assert r.status_code == 401

    def test__token_valid__fetch_successful(
        self,
        session: db.Session,
        client: FlaskClient,
        token_encoder: TokenEncoder,
    ):
        # -- Arrange ---------------------------------------------------------
        subject = 'bar'

        token = get_dummy_token(
            token_encoder=token_encoder,
            subject=subject,
            actor='foo',
            expired=False,
            scopes=['meteringpoints.read'],
        )

        mp = get_dummy_meteringpoint(
            number=1,
            include_address=False,
            include_technology=False,
        )

        insert_meteringpoint_and_delegate_access_to_subject(
            meteringpoint=mp,
            token_subject=subject,
        )

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
                'Authorization': f'Bearer: {token}'
            }
        )

        # -- Assert ----------------------------------------------------------

        # TODO: Update to check actual response error
        assert r.status_code == 200
        assert r.json['meteringpoints'][0] == make_dict_of_metering_point(mp)

    def test__subject_match_some_mps__fetch_matches_mps(
        self,
        session: db.Session,
        client: FlaskClient,
        token_encoder: TokenEncoder,
    ):
        # -- Arrange ---------------------------------------------------------
        subject = 'bar'

        token = get_dummy_token(
            token_encoder=token_encoder,
            subject=subject,
            actor='foo',
            expired=False,
            scopes=['meteringpoints.read'],
        )

        mp_1 = get_dummy_meteringpoint(
            number=1,
            include_address=False,
            include_technology=False,
        )

        mp_2 = get_dummy_meteringpoint(
            number=2,
            include_address=False,
            include_technology=False,
        )

        # Insert and delegate access
        insert_meteringpoint_and_delegate_access_to_subject(
            meteringpoint=mp_1,
            token_subject=subject,
        )

        # Insert but don't delegate access
        dispatcher(MeteringPointUpdate(
            meteringpoint=mp_2
        ))

        # -- Act -------------------------------------------------------------

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
                'Authorization': f'Bearer: {token}'
            }
        )

        # -- Assert ----------------------------------------------------------

        # TODO: Update to check actual response error
        assert r.status_code == 200
        assert len(r.json['meteringpoints']) == 1
        assert r.json['meteringpoints'][0] == make_dict_of_metering_point(mp_1)
