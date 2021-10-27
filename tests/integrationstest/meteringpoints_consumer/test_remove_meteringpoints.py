import pytest
from typing import List
from flask.testing import FlaskClient

from energytt_platform.bus import messages as m
from energytt_platform.models.meteringpoints import MeteringPoint
from energytt_platform.models.delegates import MeteringPointDelegate

from meteringpoints_consumer.handlers import dispatcher
from meteringpoints_shared.db import db


class TestOnMeteringPointUpdate:
    """
    TODO
    """

    @pytest.mark.parametrize('all_gsrn, delete_gsrn, expected_remaining_gsrn', (  # noqa: E501
        (['gsrn1', 'gsrn2', 'gsrn3'], 'gsrn1', ['gsrn2', 'gsrn3']),
        (['gsrn1', 'gsrn2', 'gsrn3'], 'FooBar', ['gsrn1', 'gsrn2', 'gsrn3']),
    ))
    def test__add_many_meteringpoints_then_remove_one__should_return_only_remaining_meteringpoints(  # noqa: E501
            self,
            all_gsrn: List[str],
            delete_gsrn: str,
            expected_remaining_gsrn: List[str],
            session: db.Session,
            client: FlaskClient,
            valid_token_encoded: str,
            token_subject: str,
    ):
        """
        TODO
        """

        # -- Act -------------------------------------------------------------

        for gsrn in all_gsrn:
            dispatcher(m.MeteringPointUpdate(
                meteringpoint=MeteringPoint(gsrn=gsrn),
            ))

            dispatcher(m.MeteringPointDelegateGranted(
                delegate=MeteringPointDelegate(
                    subject=token_subject,
                    gsrn=gsrn,
                ),
            ))

        dispatcher(m.MeteringPointRemoved(
            gsrn=delete_gsrn,
        ))

        r = client.post(
            path='/list',
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}',
            },
        )

        # -- Assert ----------------------------------------------------------

        assert r.status_code == 200
        assert r.json['success'] is True
        assert r.json['total'] == len(expected_remaining_gsrn)
        assert all(
            mp['gsrn'] in expected_remaining_gsrn
            for mp in r.json['meteringpoints']
        )
