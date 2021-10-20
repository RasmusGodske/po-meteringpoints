import pytest

from meteringpoints_shared.db import db

from energytt_platform.models.tech import Technology, TechnologyType
from energytt_platform.models.meteringpoints import MeteringPointType
from energytt_platform.models.common import Address

from meteringpoints_shared.controller import controller
from meteringpoints_shared.models import DbMeteringPoint, DbTechnology, DbMeteringPointAddress, DbMeteringPointDelegate, \
    DbMeteringPointTechnology
from meteringpoints_shared.queries import MeteringPointQuery, MeteringPointAddressQuery, MeteringPointTechnologyQuery, \
    DelegateQuery, TechnologyQuery

# ---- Seed Data -------------------------

METERINGPOINT_1_WITHOUT_TECHNOLOGY = DbMeteringPoint(
    gsrn='gsrn1',
    type=MeteringPointType.consumption,
    sector='DK1',
)

METERINGPOINT_2_WITH_TECHNOLOGY = DbMeteringPoint(
    gsrn='gsrn2',
    type=MeteringPointType.consumption,
    sector='DK2',
)

METERINGPOINT_TECHNOLGY_2 = DbMeteringPointTechnology(
    gsrn=METERINGPOINT_2_WITH_TECHNOLOGY.gsrn,
    tech_code='100',
    fuel_code='101',
)

METERINGPOINT_3_WITH_ADDRESS = DbMeteringPoint(
    gsrn='gsrn3',
    type=MeteringPointType.consumption,
    sector='DK3',
)

METERINGPOINT_ADDRESS_3 = DbMeteringPointAddress(
    gsrn=METERINGPOINT_3_WITH_ADDRESS.gsrn,
    street_code='street_code_1',
    street_name='street_name_1',
    building_number='building_number_1',
    floor_id='floor_id_1',
    room_id='room_id_1',
    post_code='post_code_1',
    city_name='city_name_1',
    city_sub_division_name='city_sub_division_name1',
    municipality_code='municipality_code_1',
    location_description='location_description_1',
)

METERINGPOINT_4_WITH_DELEGATE = DbMeteringPoint(
    gsrn='gsrn4',
    type=MeteringPointType.consumption,
    sector='DK3',
)

METERINGPOINT_DELEGATE_4 = DbMeteringPointDelegate(
    gsrn=METERINGPOINT_4_WITH_DELEGATE.gsrn,
    subject='subject',
)

METERINGPOINT_5 = DbMeteringPoint(
    gsrn='gsrn5',
    type=MeteringPointType.consumption,
    sector='DK3',

)

METERINGPOINT_TECHNOLGY_5 = DbMeteringPointTechnology(
    gsrn=METERINGPOINT_5.gsrn,
    tech_code='500',
    fuel_code='501',
)

METERINGPOINT_ADDRESS_5 = DbMeteringPointAddress(
    gsrn=METERINGPOINT_5.gsrn,
    street_code='street_code_1',
    street_name='street_name_1',
    building_number='building_number_1',
    floor_id='floor_id_1',
    room_id='room_id_1',
    post_code='post_code_1',
    city_name='city_name_1',
    city_sub_division_name='city_sub_division_name1',
    municipality_code='municipality_code_1',
    location_description='location_description_1',
)

METERINGPOINT_DELEGATE_5 = DbMeteringPointDelegate(
    gsrn=METERINGPOINT_5.gsrn,
    subject='subject5',
)

TECHNOLOGY_1 = DbTechnology(
    type=TechnologyType.nuclear,
    tech_code='001',
    fuel_code='002',
)

TECHNOLOGY_2 = DbTechnology(
    type=TechnologyType.solar,
    tech_code='011',
    fuel_code='012',
)

TECHNOLOGIES = [
    TECHNOLOGY_1,
    TECHNOLOGY_2,
]

METERINGPOINTS = [
    METERINGPOINT_1_WITHOUT_TECHNOLOGY,
    METERINGPOINT_2_WITH_TECHNOLOGY,
    METERINGPOINT_3_WITH_ADDRESS,
    METERINGPOINT_4_WITH_DELEGATE,
    METERINGPOINT_5,
]

METERINGPOINT_TECHNOLOGIES = [
    METERINGPOINT_TECHNOLGY_2,
    METERINGPOINT_TECHNOLGY_5,
]

ADDRESSES = [
    METERINGPOINT_ADDRESS_3,
    METERINGPOINT_ADDRESS_5,
]

DELEGATES = [
    METERINGPOINT_DELEGATE_4,
    METERINGPOINT_DELEGATE_5,
]


@pytest.fixture(scope='function')
def seeded_session(
        session: db.Session,
) -> db.Session:
    for meteringpoint in METERINGPOINTS:
        session.add(meteringpoint)

    for meteringpoint_technology in METERINGPOINT_TECHNOLOGIES:
        session.add(meteringpoint_technology)

    for meteringpoint_address in ADDRESSES:
        session.add(meteringpoint_address)

    for meteringpoint_delegate in DELEGATES:
        session.add(meteringpoint_delegate)

    for technology in TECHNOLOGIES:
        session.add(technology)

    session.commit()
    return session


class TestDatabaseController:
    # FIXME: Test does not work if run all at once

    # -- get_or_create_meteringpoint() ------------------------------------------------------

    @pytest.mark.parametrize('meteringpoint', (
            METERINGPOINT_1_WITHOUT_TECHNOLOGY,
            METERINGPOINT_2_WITH_TECHNOLOGY,
            METERINGPOINT_3_WITH_ADDRESS,
    ))
    def test__get_or_create_meteringpoint__does_exists__should_return(
            self,
            seeded_session: db.Session,
            meteringpoint: DbMeteringPoint,
    ):
        # -- Act -----------------------------------------------------------------

        fetched_meteringpoint = controller.get_or_create_meteringpoint(
            session=seeded_session,
            gsrn=meteringpoint.gsrn
        )

        # -- Assert --------------------------------------------------------------

        assert fetched_meteringpoint == meteringpoint

    def test__get_or_create_meteringpoint__does_not_exists__should_create_and_return_meteringpoint(
            self,
            seeded_session: db.Session,
    ):
        # -- Arrange -------------------------------------------------------------
        gsrn = 'gsrn100'

        # -- Act -----------------------------------------------------------------

        meteringpoint = controller.get_or_create_meteringpoint(
            session=seeded_session,
            gsrn=gsrn,
        )

        # Check database for new meteringpoint
        db_meteringpoint = MeteringPointQuery(seeded_session) \
            .has_gsrn(gsrn) \
            .one_or_none()

        # -- Assert --------------------------------------------------------------

        assert meteringpoint.gsrn == gsrn
        assert db_meteringpoint.gsrn == gsrn

    # -- delete_meteringpoint() ------------------------------------------------------

    @pytest.mark.parametrize('inserted_meteringpoint', (
            METERINGPOINT_1_WITHOUT_TECHNOLOGY,
            METERINGPOINT_2_WITH_TECHNOLOGY,
            METERINGPOINT_3_WITH_ADDRESS,
            METERINGPOINT_4_WITH_DELEGATE,
            METERINGPOINT_5,
    ))
    def test__delete_meteringpoint__does_exists__should_delete_meteringpoint(
            self,
            seeded_session: db.Session,
            inserted_meteringpoint: DbMeteringPoint,
    ):
        # -- Arrange -------------------------------------------------------------
        gsrn = inserted_meteringpoint.gsrn

        # -- Act -----------------------------------------------------------------

        controller.delete_meteringpoint(
            session=seeded_session,
            gsrn=gsrn,
        )

        # -- Assert --------------------------------------------------------------

        # Assert meteringpoint and all of its associated data has been deleted

        meteringpoint = MeteringPointQuery(seeded_session) \
            .has_gsrn(gsrn) \
            .one_or_none()

        address = MeteringPointAddressQuery(seeded_session) \
            .has_gsrn(gsrn) \
            .one_or_none()

        technology = MeteringPointTechnologyQuery(seeded_session) \
            .has_gsrn(gsrn) \
            .one_or_none()

        delegate = DelegateQuery(seeded_session) \
            .has_gsrn(gsrn) \
            .one_or_none()

        assert meteringpoint is None
        assert address is None
        assert technology is None
        assert delegate is None

    def test__delete_meteringpoint__does_exists__should_only_delete_one_meteringpoint(
            self,
            seeded_session: db.Session,
    ):
        # -- Arrange -------------------------------------------------------------

        # METERINGPOINT_5 is used because it contains all attributes(Address, Technology ect.)
        gsrn = METERINGPOINT_5.gsrn

        # -- Act -----------------------------------------------------------------

        controller.delete_meteringpoint(
            session=seeded_session,
            gsrn=gsrn,
        )

        # -- Assert --------------------------------------------------------------

        meteringpoints = MeteringPointQuery(seeded_session) \
            .all()

        addresses = MeteringPointAddressQuery(seeded_session) \
            .all()

        technologies = MeteringPointTechnologyQuery(seeded_session) \
            .all()

        delegates = DelegateQuery(seeded_session) \
            .all()

        # Assert that ONLY one has been deleted
        assert len(meteringpoints) == len(METERINGPOINTS) - 1
        assert len(addresses) == len(ADDRESSES) - 1
        assert len(technologies) == len(METERINGPOINT_TECHNOLOGIES) - 1
        assert len(delegates) == len(DELEGATES) - 1

    def test__delete_meteringpoint___does_not_exists__should_not_delete_anything(
            self,
            seeded_session: db.Session,
    ):
        # -- Arrange -------------------------------------------------------------

        gsrn = 'UNKNOWN_GSRN'

        # -- Act -----------------------------------------------------------------

        controller.delete_meteringpoint(
            session=seeded_session,
            gsrn=gsrn,
        )

        # -- Assert --------------------------------------------------------------

        meteringpoints = MeteringPointQuery(seeded_session) \
            .all()

        addresses = MeteringPointAddressQuery(seeded_session) \
            .all()

        technologies = MeteringPointTechnologyQuery(seeded_session) \
            .all()

        delegates = DelegateQuery(seeded_session) \
            .all()

        # If number of elements in database does not change
        # it is safe to assume nothing got deleted
        assert len(meteringpoints) == len(METERINGPOINTS)
        assert len(addresses) == len(ADDRESSES)
        assert len(technologies) == len(METERINGPOINT_TECHNOLOGIES)
        assert len(delegates) == len(DELEGATES)

    # -- set_meteringpoint_address() ------------------------------------------------------

    def test__set_meteringpoint_address__does_exists__should_update_meteringpoint_address(
            self,
            seeded_session: db.Session,
    ):
        # -- Arrange -------------------------------------------------------------

        gsrn = METERINGPOINT_3_WITH_ADDRESS.gsrn

        new_address = Address(
            street_code='new_street_code',
            street_name='new_street_name',
            building_number='new_building_number',
            floor_id='new_floor_id',
            room_id='new_room_id',
            post_code='new_post_code',
            city_name='new_city_name',
            city_sub_division_name='new_city_sub_division_nam',
            municipality_code='new_municipality_code',
            location_description='new_location_description',
        )

        # -- Act -----------------------------------------------------------------

        controller.set_meteringpoint_address(
            session=seeded_session,
            gsrn=gsrn,
            address=new_address,
        )

        address = MeteringPointAddressQuery(seeded_session) \
            .has_gsrn(gsrn) \
            .one_or_none()

        # -- Assert --------------------------------------------------------------

        address.street_code = new_address.street_code
        address.street_name = new_address.street_name
        address.building_number = new_address.building_number
        address.floor_id = new_address.floor_id
        address.room_id = new_address.room_id
        address.post_code = new_address.post_code
        address.city_name = new_address.city_name
        address.city_sub_division_name = new_address.city_sub_division_name
        address.municipality_code = new_address.municipality_code
        address.location_description = new_address.location_description

    def test__set_meteringpoint_address__does_not_exists__should_create_meteringpoint_address(
            self,
            seeded_session: db.Session,
    ):
        # -- Arrange -------------------------------------------------------------

        gsrn = 'new_gsrn_1'

        new_address = Address(
            street_code='new_street_code',
            street_name='new_street_name',
            building_number='new_building_number',
            floor_id='new_floor_id',
            room_id='new_room_id',
            post_code='new_post_code',
            city_name='new_city_name',
            city_sub_division_name='new_city_sub_division_nam',
            municipality_code='new_municipality_code',
            location_description='new_location_description',
        )

        # -- Act -----------------------------------------------------------------

        controller.set_meteringpoint_address(
            session=seeded_session,
            gsrn=gsrn,
            address=new_address,
        )

        address = MeteringPointAddressQuery(seeded_session) \
            .has_gsrn(gsrn) \
            .one_or_none()

        # -- Assert --------------------------------------------------------------

        address.street_code = new_address.street_code
        address.street_name = new_address.street_name
        address.building_number = new_address.building_number
        address.floor_id = new_address.floor_id
        address.room_id = new_address.room_id
        address.post_code = new_address.post_code
        address.city_name = new_address.city_name
        address.city_sub_division_name = new_address.city_sub_division_name
        address.municipality_code = new_address.municipality_code
        address.location_description = new_address.location_description

    # -- delete_meteringpoint_address() ------------------------------------------------------

    def test__delete_meteringpoint_address__does_exists__should_delete_correct(
            self,
            seeded_session: db.Session,
    ):
        # -- Arrange -------------------------------------------------------------

        gsrn = METERINGPOINT_3_WITH_ADDRESS.gsrn

        # -- Act -----------------------------------------------------------------

        controller.delete_meteringpoint_address(
            session=seeded_session,
            gsrn=gsrn,
        )

        # -- Assert --------------------------------------------------------------

        address = MeteringPointAddressQuery(seeded_session) \
            .has_gsrn(gsrn) \
            .one_or_none()

        assert address is None

    def test__delete_meteringpoint_address__does_exists__should_only_delete_one(
            self,
            seeded_session: db.Session,
    ):
        # -- Arrange -------------------------------------------------------------

        gsrn = METERINGPOINT_3_WITH_ADDRESS.gsrn

        # -- Act -----------------------------------------------------------------

        controller.delete_meteringpoint_address(
            session=seeded_session,
            gsrn=gsrn,
        )

        # -- Assert --------------------------------------------------------------

        addresses = MeteringPointAddressQuery(seeded_session) \
            .all()

        # Assert that ONLY one has been deleted
        assert len(addresses) == len(ADDRESSES) - 1

    def test__delete_meteringpoint_address__does_not_exists__should_not_delete_anything(
            self,
            seeded_session: db.Session,
    ):
        # -- Arrange -------------------------------------------------------------

        gsrn = 'unknown_gsrn'

        # -- Act -----------------------------------------------------------------

        controller.delete_meteringpoint_address(
            session=seeded_session,
            gsrn=gsrn,
        )

        # -- Assert --------------------------------------------------------------

        addresses = MeteringPointAddressQuery(seeded_session) \
            .all()

        assert len(addresses) == len(ADDRESSES)

    # -- grant_meteringpoint_delegate() ------------------------------------------------------

    def test__grant_meteringpoint_delegate__does_exists__should_not_change_anything(
            self,
            seeded_session: db.Session,
    ):
        # -- Arrange -------------------------------------------------------------

        gsrn = METERINGPOINT_DELEGATE_4.gsrn
        subject = METERINGPOINT_DELEGATE_4.subject

        # -- Act -----------------------------------------------------------------

        controller.grant_meteringpoint_delegate(
            session=seeded_session,
            gsrn=gsrn,
            subject=subject,
        )

        delegate = DelegateQuery(seeded_session) \
            .has_gsrn(gsrn) \
            .has_subject(subject) \
            .one_or_none()

        # -- Assert --------------------------------------------------------------

        assert delegate.subject is subject
        assert delegate.gsrn is gsrn

    def test__grant_meteringpoint_delegate__does_not_exists__should_create_delegate(
            self,
            seeded_session: db.Session,
    ):
        # -- Arrange -------------------------------------------------------------

        gsrn = 'new_gsrn'
        subject = 'new_subject'

        # -- Act -----------------------------------------------------------------

        controller.grant_meteringpoint_delegate(
            session=seeded_session,
            gsrn=gsrn,
            subject=subject,
        )

        delegate = DelegateQuery(seeded_session) \
            .has_gsrn(gsrn) \
            .has_subject(subject) \
            .one_or_none()

        # -- Assert --------------------------------------------------------------

        assert delegate.subject == subject
        assert delegate.gsrn == gsrn

    # -- revoke_meteringpoint_delegate() ------------------------------------------------------

    def test__revoke_meteringpoint_delegate__does_exists__should_delete_delegate(
            self,
            seeded_session: db.Session,
    ):
        # -- Arrange -------------------------------------------------------------

        gsrn = METERINGPOINT_DELEGATE_4.gsrn
        subject = METERINGPOINT_DELEGATE_4.subject

        # -- Act -----------------------------------------------------------------

        controller.revoke_meteringpoint_delegate(
            session=seeded_session,
            gsrn=gsrn,
            subject=subject,
        )

        # -- Assert --------------------------------------------------------------

        delegate_exists = DelegateQuery(seeded_session) \
            .has_gsrn(gsrn) \
            .has_subject(subject) \
            .exists()

        assert delegate_exists is False

    def test__revoke_meteringpoint_delegate__unknown_subject_and_known_gsrn__should_not_delete_anything(
            self,
            seeded_session: db.Session,
    ):
        # -- Arrange -------------------------------------------------------------

        gsrn = METERINGPOINT_DELEGATE_4.gsrn
        subject = 'unknown_gsrn'

        # -- Act -----------------------------------------------------------------

        controller.revoke_meteringpoint_delegate(
            session=seeded_session,
            gsrn=gsrn,
            subject=subject,
        )

        # -- Assert --------------------------------------------------------------

        delegates = DelegateQuery(seeded_session) \
            .all()

        assert len(delegates) == len(DELEGATES)

    def test__revoke_meteringpoint_delegate__known_subject_and_unknown_gsrn__should_not_delete_anything(
            self,
            seeded_session: db.Session,
    ):
        # -- Arrange -------------------------------------------------------------

        gsrn = 'unknown_gsrn'
        subject = METERINGPOINT_DELEGATE_4.subject

        # -- Act -----------------------------------------------------------------

        controller.revoke_meteringpoint_delegate(
            session=seeded_session,
            gsrn=gsrn,
            subject=subject,
        )

        # -- Assert --------------------------------------------------------------

        delegates = DelegateQuery(seeded_session) \
            .all()

        assert len(delegates) == len(DELEGATES)

    def test__revoke_meteringpoint_delegate__does_not_exists__should_not_delete_anything(
            self,
            seeded_session: db.Session,
    ):
        # -- Arrange -------------------------------------------------------------

        gsrn = 'unknown_gsrn'
        subject = 'unknown_subject'

        # -- Act -----------------------------------------------------------------

        controller.revoke_meteringpoint_delegate(
            session=seeded_session,
            gsrn=gsrn,
            subject=subject,
        )

        # # -- Assert --------------------------------------------------------------

        delegates = DelegateQuery(seeded_session) \
            .all()

        assert len(delegates) == len(DELEGATES)

    # -- set_meteringpoint_technology() ------------------------------------------------------

    def test__set_meteringpoint_technology__does_exists__should_update_meteringpoint_technology(
            self,
            seeded_session: db.Session,
    ):
        # -- Arrange -------------------------------------------------------------

        gsrn = METERINGPOINT_2_WITH_TECHNOLOGY.gsrn

        new_technology = Technology(
            type=TechnologyType.nuclear,
            tech_code='900',
            fuel_code='901',
        )

        # -- Act -----------------------------------------------------------------

        controller.set_meteringpoint_technology(
            session=seeded_session,
            gsrn=gsrn,
            technology=new_technology,
        )

        meteringpoint_technology = MeteringPointTechnologyQuery(seeded_session) \
            .has_gsrn(gsrn) \
            .one_or_none()

        # -- Assert --------------------------------------------------------------

        assert meteringpoint_technology.tech_code == new_technology.tech_code
        assert meteringpoint_technology.fuel_code == new_technology.fuel_code

    def test__set_meteringpoint_technology__does_not_exists__should_create_meteringpoint_technology(  # noqa: E501
            self,
            seeded_session: db.Session,
    ):
        # -- Arrange -------------------------------------------------------------

        gsrn = METERINGPOINT_1_WITHOUT_TECHNOLOGY.gsrn

        new_technology = Technology(
            type=TechnologyType.nuclear,
            tech_code='900',
            fuel_code='901',
        )

        # -- Act -----------------------------------------------------------------

        controller.set_meteringpoint_technology(
            session=seeded_session,
            gsrn=gsrn,
            technology=new_technology,
        )

        meteringpoint_technology = MeteringPointTechnologyQuery(seeded_session) \
            .has_gsrn(gsrn) \
            .one_or_none()

        # -- Assert --------------------------------------------------------------

        assert meteringpoint_technology.tech_code == new_technology.tech_code
        assert meteringpoint_technology.fuel_code == new_technology.fuel_code

    # -- delete_meteringpoint_technology() ------------------------------------------------------

    def test__delete_meteringpoint_technology__does_exists__should_delete_correct(
            self,
            seeded_session: db.Session,
    ):
        # -- Arrange -------------------------------------------------------------

        gsrn = METERINGPOINT_2_WITH_TECHNOLOGY.gsrn

        # -- Act -----------------------------------------------------------------

        controller.delete_meteringpoint_technology(
            session=seeded_session,
            gsrn=gsrn,
        )

        # -- Assert --------------------------------------------------------------

        meteringpoint_technology_exists = MeteringPointTechnologyQuery(seeded_session) \
            .has_gsrn(gsrn) \
            .exists()

        assert meteringpoint_technology_exists is False

    def test__delete_meteringpoint_technology__does_exists__should_only_delete_one(
            self,
            seeded_session: db.Session,
    ):
        # -- Arrange -------------------------------------------------------------

        gsrn = METERINGPOINT_2_WITH_TECHNOLOGY.gsrn

        # -- Act -----------------------------------------------------------------

        controller.delete_meteringpoint_technology(
            session=seeded_session,
            gsrn=gsrn,
        )

        # -- Assert --------------------------------------------------------------

        meteringpoint_technologies = MeteringPointTechnologyQuery(seeded_session) \
            .all()

        # Assert that ONLY one has been deleted
        assert len(meteringpoint_technologies) == len(METERINGPOINT_TECHNOLOGIES) - 1

    def test__delete_meteringpoint_technology__does_not_exists__should_not_delete_anything(
            self,
            seeded_session: db.Session,
    ):
        # -- Arrange -------------------------------------------------------------

        gsrn = 'unknown_gsrn'

        # -- Act -----------------------------------------------------------------

        controller.delete_meteringpoint_technology(
            session=seeded_session,
            gsrn=gsrn,
        )

        # -- Assert --------------------------------------------------------------

        meteringpoint_technologies = MeteringPointTechnologyQuery(seeded_session) \
            .all()

        assert len(meteringpoint_technologies) == len(METERINGPOINT_TECHNOLOGIES)

    # -- get_or_create_technology() ------------------------------------------------------

    def test__get_or_create_technology__does_exists__should_return_technology(
            self,
            seeded_session: db.Session,
    ):
        # -- Act -----------------------------------------------------------------

        fetched_technology = controller.get_or_create_technology(
            session=seeded_session,
            tech_code=TECHNOLOGY_1.tech_code,
            fuel_code=TECHNOLOGY_1.fuel_code,
        )

        # -- Assert --------------------------------------------------------------

        assert fetched_technology == TECHNOLOGY_1

    def test__get_or_create_technology__does_not_exists__should_return_technology(
            self,
            session: db.Session,
    ):
        # -- Arrange -------------------------------------------------------------
        new_technology = DbTechnology(
            tech_code='222',
            fuel_code='333',
        )

        # -- Act -----------------------------------------------------------------

        returned_technology = controller.get_or_create_technology(
            session=session,
            tech_code=new_technology.tech_code,
            fuel_code=new_technology.fuel_code,
        )

        fetched_technology = TechnologyQuery(session) \
            .has_tech_code(new_technology.tech_code) \
            .has_fuel_code(new_technology.fuel_code) \
            .one_or_none()

        # -- Assert --------------------------------------------------------------

        assert returned_technology.tech_code == new_technology.tech_code
        assert returned_technology.fuel_code == new_technology.fuel_code

        assert fetched_technology.tech_code == new_technology.tech_code
        assert fetched_technology.fuel_code == new_technology.fuel_code

    # -- delete_technology() ------------------------------------------------------

    def test__delete_technology__does_exists__should_delete(
            self,
            seeded_session: db.Session,
    ):
        # -- Arrange -------------------------------------------------------------

        tech_code = TECHNOLOGY_1.tech_code
        fuel_code = TECHNOLOGY_1.fuel_code

        # -- Act -----------------------------------------------------------------

        controller.delete_technology(
            session=seeded_session,
            tech_code=tech_code,
            fuel_code=fuel_code,
        )

        # -- Assert --------------------------------------------------------------

        technology_exists = TechnologyQuery(seeded_session) \
            .has_tech_code(tech_code) \
            .has_fuel_code(fuel_code) \
            .exists()

        assert technology_exists is False

    def test__delete_technology__does_exists__should_only_delete_one(
            self,
            seeded_session: db.Session,
    ):
        # -- Act -----------------------------------------------------------------

        controller.delete_technology(
            session=seeded_session,
            tech_code=TECHNOLOGY_1.tech_code,
            fuel_code=TECHNOLOGY_1.fuel_code,
        )

        # -- Assert --------------------------------------------------------------

        technologies = TechnologyQuery(seeded_session) \
            .all()

        # Assert that ONLY one has been deleted
        assert len(technologies) == len(TECHNOLOGIES) - 1
