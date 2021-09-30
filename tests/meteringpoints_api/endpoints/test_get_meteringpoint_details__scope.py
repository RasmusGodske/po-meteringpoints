from flask.testing import FlaskClient

from meteringpoints_shared.db import db

from energytt_platform.tokens import TokenEncoder

from ...helpers import \
    get_dummy_token, \
    insert_meteringpoint_and_delegate_access_to_subject, \
    make_dict_of_metering_point, \
    get_dummy_meteringpoint


class TestGetMeteringPointDetailsScope:
    def test__scope_read_type_in_token__able_to_fetch_mp(
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

        assert r.status_code == 200
        assert r.json['meteringpoint'] == make_dict_of_metering_point(mp)

    def test__scope_non_existen__unable_to_fetch_mp(
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
            scopes=[],
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
        assert r.status_code == 401

    def test__scope_is_invalid__unable_to_fetch_mp(
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
            scopes=['this_is_a_invalid_scope'],
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
        assert r.status_code == 401
