from flask.testing import FlaskClient

from energytt_platform.bus.messages.delegates import \
    MeteringPointDelegateGranted, \
    MeteringPointDelegateRevoked
from energytt_platform.models.delegates import MeteringPointDelegate

from meteringpoints_shared.db import db

from meteringpoints_consumer.handlers import dispatcher
from energytt_platform.bus.messages.meteringpoints import \
    MeteringPointUpdate

from ...helpers import \
    make_dict_of_metering_point, \
    insert_technology_from_meteringpoint, \
    get_dummy_meteringpoint, \
    get_dummy_meteringpoint_list


class TestMeteringPointDelegateRevoked:
    def test__grant_access_to_gsrn_then_revoke_it__not_able_to_fetch_mp(
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
            include_technology=False,
        )

        dispatcher(MeteringPointUpdate(
            meteringpoint=mp
        ))

        dispatcher(MeteringPointDelegateGranted(
            delegate=MeteringPointDelegate(
                subject=subject,
                gsrn=mp.gsrn,
            )
        ))

        # -- Act -------------------------------------------------------------

        dispatcher(MeteringPointDelegateRevoked(
            delegate=MeteringPointDelegate(
                subject=subject,
                gsrn=mp.gsrn,
            )
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

    def test__grant_access_then_revoke_for_half__fetched_mps_with_access(
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
            include_technology=True,
        )

        # List of meteringpoints into two lists
        granted_mp_list = mp_list[:len(mp_list)//2]
        non_granted_mp_list = mp_list[len(mp_list)//2:]

        granted_mp_gsrn_list = [o.gsrn for o in granted_mp_list]
        non_granted_mp_gsrn_list = [o.gsrn for o in non_granted_mp_list]

        all_gsrn_list = granted_mp_gsrn_list + non_granted_mp_gsrn_list

        for meteringpoint in granted_mp_list:
            insert_technology_from_meteringpoint(
                meteringpoint=meteringpoint
            )

        # -- Act -------------------------------------------------------------

        # Insert meteringpoints and grant access
        for mp in mp_list:
            dispatcher(MeteringPointUpdate(
                meteringpoint=mp
            ))

            dispatcher(MeteringPointDelegateGranted(
                delegate=MeteringPointDelegate(
                    subject=subject,
                    gsrn=mp.gsrn,
                )
            ))

        # revoke grant to som meteringpoints
        for mp in non_granted_mp_list:
            dispatcher(MeteringPointDelegateRevoked(
                delegate=MeteringPointDelegate(
                    subject=subject,
                    gsrn=mp.gsrn,
                )
            ))

        r = client.post(
            path='/list',
            json={
                'offset': 0,
                'limit': 10,
                'filters': {
                    'gsrn': all_gsrn_list,  # Attempt to fetch all mps
                },
            },
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}',
            }
        )

        # -- Assert ----------------------------------------------------------

        assert len(r.json['meteringpoints']) == len(granted_mp_gsrn_list)

        expected_mp_dict = {
            m.gsrn: m for m in mp_list
            if m.gsrn in granted_mp_gsrn_list
        }

        # Validate that the inserted metering points is also fetched
        for meteringpoint in r.json['meteringpoints']:
            expected = expected_mp_dict[meteringpoint["gsrn"]]
            assert meteringpoint == make_dict_of_metering_point(expected)
