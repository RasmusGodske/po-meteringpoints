from flask.testing import FlaskClient

from energytt_platform.bus.messages.tech import \
    TechnologyRemoved, TechnologyUpdate
from energytt_platform.models.tech import Technology, TechnologyType

from meteringpoints_consumer.handlers import dispatcher
from meteringpoints_shared.db import db

from ...helpers import \
    get_dummy_meteringpoint_list, \
    insert_meteringpoint_and_delegate_access_to_subject, \
    get_dummy_meteringpoint


class TestTechnologyRemoved:

    def test__add_technology_then_remove__fetched_mp_technology_is_none(
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

        dispatcher(TechnologyUpdate(
            technology=mp.technology
        ))

        # -- Act -------------------------------------------------------------

        dispatcher(TechnologyRemoved(
            codes=mp.technology
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

        assert fetched_mp['technology'] is None

    def test__add_multiple_mps_remove_technology__mp_technology_is_none(
            self,
            session: db.Session,
            client: FlaskClient,
            valid_token_encoded: str,
    ):
        # -- Arrange ---------------------------------------------------------

        subject = 'bar'

        meteringpoint_count = 10

        mp_list = get_dummy_meteringpoint_list(
            count=meteringpoint_count,
            include_address=True,
            include_technology=False,
        )

        mp_gsrn_list = [o.gsrn for o in mp_list]

        technology = Technology(
            tech_code="100",
            fuel_code='200',
            type=TechnologyType.coal,
        )

        dispatcher(TechnologyUpdate(
            technology=technology
        ))

        for mp in mp_list:
            # Populate with technology
            mp.technology = technology

            insert_meteringpoint_and_delegate_access_to_subject(
                meteringpoint=mp,
                token_subject=subject,
            )

        # -- Act -------------------------------------------------------------

        dispatcher(TechnologyRemoved(
            codes=technology
        ))

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
                'Authorization': f'Bearer: {valid_token_encoded}'
            }
        )

        # -- Assert ----------------------------------------------------------

        assert r.status_code == 200
        assert len(r.json['meteringpoints']) == len(mp_list)

        fetched_mp_list = r.json['meteringpoints']

        for mp in fetched_mp_list:
            assert mp['technology'] is None
