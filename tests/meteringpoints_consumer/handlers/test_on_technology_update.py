from energytt_platform.bus.messages import tech
from energytt_platform.bus.messages.tech import TechnologyUpdate
from energytt_platform.models.tech import Technology, TechnologyType
from flask.testing import FlaskClient

from energytt_platform.bus.messages.meteringpoints import MeteringPointUpdate

from meteringpoints_consumer.handlers import dispatcher

from meteringpoints_shared.db import db

from ...helpers import \
    insert_meteringpoint_and_delegate_access_to_subject, \
    insert_meteringpoint_and_delegate_access_to_subject, \
    make_dict_of_metering_point, \
    get_dummy_meteringpoint


class TestOnTechnologyUpdate:

    def test__add_technology__fetched_mp_contains_technology(
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

        insert_meteringpoint_and_delegate_access_to_subject(
            meteringpoint=mp,
            token_subject=subject,
        )

        # -- Act -------------------------------------------------------------

        dispatcher(TechnologyUpdate(
            technology=mp.technology
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

        expected_result = make_dict_of_metering_point(mp)
        fetched_mp = r.json['meteringpoints'][0]

        assert fetched_mp['technology'] == expected_result['technology']

    def test__add_mp_without_technology__fetched_mp_technology_is_none(
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
                'Authorization': f'Bearer: {valid_token_encoded}'
            }
        )

        # -- Assert ----------------------------------------------------------

        assert r.status_code == 200
        assert len(r.json['meteringpoints']) == 1

        fetched_mp = r.json['meteringpoints'][0]

        assert fetched_mp['technology'] is None

    def test__update_technology_type__technology_type_updated(
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

        technology = Technology(
            tech_code="100",
            fuel_code="200",
            type=TechnologyType.coal,
        )

        mp.technology = technology

        insert_meteringpoint_and_delegate_access_to_subject(
            meteringpoint=mp,
            token_subject=subject,
        )

        dispatcher(TechnologyUpdate(
            technology=technology
        ))

        # -- Act -------------------------------------------------------------

        # Update technology.type

        technology.type = TechnologyType.wind

        dispatcher(TechnologyUpdate(
            technology=technology
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

        fetched_mp = r.json['meteringpoints'][0]

        assert fetched_mp['technology'] == {
            'fuel_code': technology.fuel_code,
            'tech_code': technology.tech_code,
            'type': technology.type.value,
        }
