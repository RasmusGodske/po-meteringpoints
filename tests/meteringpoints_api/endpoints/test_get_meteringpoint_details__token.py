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


class TestGetMeteringPointDetailsToken:
    def test__no_token__expect_error(
        self,
        session: db.Session,
        client: FlaskClient,
        token_encoder: TokenEncoder,
    ):
        # -- Arrange ---------------------------------------------------------

        # -- Act -------------------------------------------------------------

        r = client.get(
            path='/details',
            query_string={
                'gsrn': 'GSRN#1'
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

        r = client.get(
            path='/details',
            query_string={
                'gsrn': 'GSRN#1'
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

        r = client.get(
            path='/details',
            query_string={
                'gsrn': 'GSRN#1'
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

        r = client.get(
            path='/details',
            query_string={
                'gsrn': 'GSRN#1'
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

        r = client.get(
            path='/details',
            query_string={
                'gsrn': mp.gsrn,
            },
            headers={
                'Authorization': f'Bearer: {token}'
            }
        )

        # -- Assert ----------------------------------------------------------

        # TODO: Update to check actual response error
        assert r.status_code == 200
        assert r.json['meteringpoint'] == make_dict_of_metering_point(mp)

    def test__subject_match_mp__fetch_mp_successfully(
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
            actor='bar',
            expired=False,
            scopes=['meteringpoints.read'],
        )

        mp = get_dummy_meteringpoint(
            number=1,
            include_address=False,
            include_technology=False,
        )

        # Insert and delegate access
        insert_meteringpoint_and_delegate_access_to_subject(
            meteringpoint=mp,
            token_subject=subject,
        )

        # -- Act -------------------------------------------------------------

        r = client.get(
            path='/details',
            query_string={
                'gsrn': mp.gsrn,
            },
            headers={
                'Authorization': f'Bearer: {token}'
            }
        )

        # -- Assert ----------------------------------------------------------

        assert r.status_code == 200
        assert r.json['meteringpoint'] == make_dict_of_metering_point(mp)
