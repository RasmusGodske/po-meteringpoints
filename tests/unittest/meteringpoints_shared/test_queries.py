from typing import List

import pytest
from itertools import product

from energytt_platform.models.common import Order
from energytt_platform.models.meteringpoints import MeteringPoint

from meteringpoints_shared.db import db
from energytt_platform.models.meteringpoints import MeteringPointType

from meteringpoints_shared.models import (
    DbMeteringPoint,
    DbMeteringPointDelegate, MeteringPointFilters, MeteringPointOrdering, MeteringPointOrderingKeys,
    DbMeteringPointAddress, DbMeteringPointTechnology, DbTechnology,
)
from meteringpoints_shared.queries import MeteringPointQuery, MeteringPointAddressQuery, MeteringPointTechnologyQuery, \
    DelegateQuery, TechnologyQuery


class TestMeteringPointQuery:
    TYPES = (MeteringPointType.consumption, MeteringPointType.production)
    SECTORS = ('DK1', 'DK2')
    COMBINATIONS = list(product(TYPES, SECTORS))

    @pytest.fixture(scope='function')
    def seed_meteringpoints(self) -> List[MeteringPoint]:
        """
        TODO

        :return:
        """

        mp_list = []

        for i, (type, sector) in enumerate(self.COMBINATIONS):
            mp_list.append(DbMeteringPoint(
                gsrn=f'gsrn{i}',
                type=type,
                sector=sector,
            ))

        return mp_list

    @pytest.fixture(scope='function')
    def seeded_session(
            self,
            session: db.Session,
            seed_meteringpoints: List[MeteringPoint],
            token_subject: str,
    ) -> db.Session:
        """
        TODO
        """
        session.begin()

        for meteringpoint in seed_meteringpoints:
            session.add(DbMeteringPoint(
                gsrn=meteringpoint.gsrn,
                type=meteringpoint.type,
                sector=meteringpoint.sector,
            ))

        session.commit()

        yield session

    @pytest.mark.parametrize('gsrn', ('gsrn0', 'gsrn1', 'gsrn2'))
    def test__has_gsrn__gsrn_exists__should_return_correct_meteringpoint(
            self,
            seeded_session: db.Session,
            gsrn: str,
    ):
        # -- Act -------------------------------------------------------------

        query = MeteringPointQuery(seeded_session) \
            .has_gsrn(gsrn)

        # -- Assert ----------------------------------------------------------

        assert query.count() == 1
        assert query.one().gsrn == gsrn

    @pytest.mark.parametrize('gsrn', ('unknown_gsrn_1', None))
    def test__has_gsrn__gsrn_does_not_exists__should_return_no_meteringpoints(
            self,
            seeded_session: db.Session,
            gsrn: str,
    ):
        # -- Act -------------------------------------------------------------

        query = MeteringPointQuery(seeded_session) \
            .has_gsrn(gsrn)

        # -- Assert ----------------------------------------------------------

        assert query.count() == 0

    @pytest.mark.parametrize('gsrn, expected_gsrn_returned', (
            (['gsrn0'], ['gsrn0']),
            (['gsrn0', 'gsrn1'], ['gsrn0', 'gsrn1']),
            (['unknown_gsrn_1'], []),
            (['unknown_gsrn_1', 'gsrn1'], ['gsrn1']),
            ([], []),
    ))
    def test__has_any_gsrn__should_return_correct_meteringpoints(
            self,
            seeded_session: db.Session,
            gsrn: List[str],
            expected_gsrn_returned: List[str],
    ):
        # -- Act -------------------------------------------------------------

        query = MeteringPointQuery(seeded_session) \
            .has_any_gsrn(gsrn)

        # -- Assert ----------------------------------------------------------

        assert query.count() == len(expected_gsrn_returned)
        assert all(mp.gsrn in expected_gsrn_returned for mp in query.all())

    @pytest.mark.parametrize('meteringpoint_type', (
            MeteringPointType.consumption,
            MeteringPointType.production,
    ))
    def test__is_type__should_return_correct_meteringpoints(
            self,
            seeded_session: db.Session,
            meteringpoint_type: MeteringPointType,
    ):
        # -- Act -------------------------------------------------------------

        query = MeteringPointQuery(seeded_session) \
            .is_type(meteringpoint_type)

        # -- Assert ----------------------------------------------------------

        assert query.count() > 0
        assert all(mp.type is meteringpoint_type for mp in query.all())

    @pytest.mark.parametrize('sector', (
            'DK1',
    ))
    def test__in_sector__sector_exists__should_return_correct_meteringpoints(
            self,
            seeded_session: db.Session,
            seed_meteringpoints: List[MeteringPoint],
            sector: str,
    ):
        # -- Act - ------------------------------------------------------------

        query = MeteringPointQuery(seeded_session) \
            .in_sector(sector)

        # -- Assert ----------------------------------------------------------

        assert query.count() == len([mp for mp in seed_meteringpoints if mp.sector == sector])
        assert all(mp.sector == sector for mp in query.all())

    @pytest.mark.parametrize('sector', (
            '',
            'unknown_sector',
    ))
    def test__in_sector__sector_does_not_exist__should_return_nothing(
            self,
            seeded_session: db.Session,
            seed_meteringpoints: List[MeteringPoint],
            sector: str,
    ):
        # -- Act - ------------------------------------------------------------

        query = MeteringPointQuery(seeded_session) \
            .in_sector(sector)

        # -- Assert ----------------------------------------------------------

        assert query.count() == 0

    @pytest.mark.parametrize('sectors', (
            ['DK1'],
            ['DK1', 'DK2'],
            ['unknown_sector'],
            ['DK1', 'unknown_sector'],
            ['DK1', 'DK1'],
            [''],
            [],
    ))
    def test__in_any_sector__should_return_correct_meteringpoints(
            self,
            seeded_session: db.Session,
            seed_meteringpoints: List[MeteringPoint],
            sectors: List[str],
    ):
        # -- Act -------------------------------------------------------------

        query = MeteringPointQuery(seeded_session) \
            .in_any_sector(sectors)

        # -- Assert ----------------------------------------------------------

        assert query.count() == len([mp for mp in seed_meteringpoints if mp.sector in sectors])
        assert all(meteringpoint.sector in sectors for meteringpoint in query.all())

    @pytest.mark.parametrize('gsrn_with_delegated_access', (
            ['gsrn1'],
            ['gsrn1', 'gsrn2'],
            [],
    ))
    def test__is_accessible_by__should_return_meteringpoints_with_delegated_access(
            self,
            seeded_session: db.Session,
            seed_meteringpoints: List[MeteringPoint],
            gsrn_with_delegated_access: List[str],
    ):
        # -- Arrange ---------------------------------------------------------

        subject = 'subject1'

        # -- Act -------------------------------------------------------------

        for gsrn in gsrn_with_delegated_access:
            seeded_session.add(DbMeteringPointDelegate(
                gsrn=gsrn,
                subject=subject,
            ))
        seeded_session.commit()

        query = MeteringPointQuery(seeded_session) \
            .is_accessible_by(subject)

        # -- Assert ----------------------------------------------------------

        assert query.count() == len(gsrn_with_delegated_access)
        assert all(mp.gsrn in gsrn_with_delegated_access for mp in query.all())

    @pytest.mark.parametrize('filters', (
            MeteringPointFilters(),
            MeteringPointFilters(gsrn=['gsrn1']),
            MeteringPointFilters(gsrn=['gsrn1', 'gsrn2']),
            MeteringPointFilters(type=MeteringPointType.production),
            MeteringPointFilters(type=MeteringPointType.consumption),
            MeteringPointFilters(sector=['DK1']),
            MeteringPointFilters(sector=['DK1', 'DK2']),
    ))
    def test__query_apply_filters__meteringpoints_match_filters__should_return_correct_meteringpoints(
            self,
            seeded_session: db.Session,
            filters: MeteringPointFilters,
            seed_meteringpoints: List[MeteringPoint],
    ):

        # -- Act -------------------------------------------------------------

        results = MeteringPointQuery(seeded_session) \
            .apply_filters(filters) \
            .all()

        # -- Assert -------------------------------------------------------------

        assert len(results) > 0

        if filters.gsrn is not None:
            assert all(mp.gsrn in filters.gsrn for mp in results)

        if filters.type is not None:
            assert all(mp.type is filters.type for mp in results)

        if filters.sector is not None:
            assert all(mp.sector in filters.sector for mp in results)

    @pytest.mark.parametrize('filters', (
            MeteringPointFilters(gsrn=[]),
            MeteringPointFilters(gsrn=['UNKNOWN_GSRN']),
            MeteringPointFilters(sector=[]),
            MeteringPointFilters(sector=['UNKNOWN_SECTOR']),
    ))
    def test__query_apply_filters__meteringpoints_does_not_match_filters__should_return_no_meteringpoints(
            self,
            seeded_session: db.Session,
            filters: MeteringPointFilters,
            seed_meteringpoints: List[MeteringPoint],
    ):

        # -- Act -------------------------------------------------------------

        results = MeteringPointQuery(seeded_session) \
            .apply_filters(filters) \
            .all()

        # -- Assert -------------------------------------------------------------

        assert len(results) == 0

    @pytest.mark.parametrize('ordering', (
            MeteringPointOrdering(key=MeteringPointOrderingKeys.gsrn, order=Order.asc),
            MeteringPointOrdering(key=MeteringPointOrderingKeys.gsrn, order=Order.desc),
            MeteringPointOrdering(key=MeteringPointOrderingKeys.sector, order=Order.asc),
            MeteringPointOrdering(key=MeteringPointOrderingKeys.sector, order=Order.desc),
    ))
    def test__apply_ordering__should_return_correct_meteringpoints(
            self,
            seeded_session: db.Session,
            ordering: MeteringPointOrdering,
            seed_meteringpoints: List[MeteringPoint],
    ):
        # -- Act -------------------------------------------------------------

        results = MeteringPointQuery(seeded_session) \
            .apply_ordering(ordering) \
            .all()

        # -- Assert ----------------------------------------------------------

        sort_descending = ordering.order == Order.desc

        if ordering.key is MeteringPointOrderingKeys.gsrn:
            f = lambda mp: mp.gsrn
        elif ordering.key is MeteringPointOrderingKeys.sector:
            f = lambda mp: mp.sector
        else:
            raise RuntimeError('Should not happen')

        assert len(results) == len(seed_meteringpoints)
        assert [mp.gsrn for mp in results] == \
               [mp.gsrn for mp in sorted(seed_meteringpoints,
                                         key=f, reverse=sort_descending)]


class TestMeteringPointAddressQuery:
    def test__has_gsrn__gsrn_exists__should_return_correct_meteringpointaddress(
            self,
            session: db.Session,
    ):
        # -- Arrange -------------------------------------------------------------

        gsrn = 'gsrn1'

        session.add(DbMeteringPoint(
            gsrn=gsrn,
            type=MeteringPointType.consumption,
            sector='DK1',
        ))

        session.add(DbMeteringPointAddress(
            gsrn=gsrn,
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
        ))

        session.commit()

        # -- Act -----------------------------------------------------------------

        result = MeteringPointAddressQuery(session) \
            .has_gsrn(gsrn) \
            .all()

        # -- Assert --------------------------------------------------------------

        assert len(result) == 1
        assert result[0].gsrn == gsrn

    @pytest.mark.parametrize('gsrn', ('unknown_gsrn_1', None))
    def test__has_gsrn__gsrn_does_not_exists__should_not_return_any_meteringpointaddress(
            self,
            session: db.Session,
            gsrn: str,
    ):
        # -- Arrange -------------------------------------------------------------

        session.add(DbMeteringPoint(
            gsrn='gsrn1',
            type=MeteringPointType.consumption,
            sector='DK1',
        ))

        session.add(DbMeteringPointAddress(
            gsrn='gsrn1',
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
        ))

        session.commit()

        # -- Act -----------------------------------------------------------------

        result = MeteringPointAddressQuery(session) \
            .has_gsrn(gsrn) \
            .all()

        # -- Assert --------------------------------------------------------------

        assert len(result) == 0


class TestMeteringPointTechnologyQuery:
    def test__has_gsrn__gsrn_exists__should_return_correct_meteringpointtechnology(
            self,
            session: db.Session,
    ):
        # -- Arrange -------------------------------------------------------------

        gsrn = 'gsrn1'

        session.add(DbMeteringPoint(
            gsrn=gsrn,
            type=MeteringPointType.consumption,
            sector='DK1',
        ))

        session.add(DbMeteringPointTechnology(
            gsrn=gsrn,
            tech_code='100',
            fuel_code='102',
        ))

        session.commit()

        # -- Act -----------------------------------------------------------------

        result = MeteringPointTechnologyQuery(session) \
            .has_gsrn(gsrn) \
            .all()

        # -- Assert --------------------------------------------------------------

        assert len(result) == 1
        assert result[0].gsrn == gsrn

    @pytest.mark.parametrize('gsrn', ('unknown_gsrn_1', None))
    def test__has_gsrn__gsrn_does_not_exists__should_not_return_any_meteringpointtechnology(
            self,
            session: db.Session,
            gsrn: str,
    ):
        # -- Arrange -------------------------------------------------------------

        session.add(DbMeteringPoint(
            gsrn='gsrn1',
            type=MeteringPointType.consumption,
            sector='DK1',
        ))

        session.add(DbMeteringPointTechnology(
            gsrn='gsrn1',
            tech_code='100',
            fuel_code='102',
        ))

        session.commit()

        # -- Act -----------------------------------------------------------------

        result = MeteringPointTechnologyQuery(session) \
            .has_gsrn(gsrn) \
            .all()

        # -- Assert --------------------------------------------------------------

        assert len(result) == 0


class TestDelegateQuery:
    # FIXME: Following tests fails when running with the other tests, but succeed when running alone
    #  - test__has_subject__single_subject_exists__should_return_correct_delegate
    #  - test__has_subject__single_subject_exists__should_return_correct_delegate
    DELEGATE_1 = DbMeteringPointDelegate(
        gsrn='gsrn1',
        subject='subject1',
    )

    DELEGATE_2 = DbMeteringPointDelegate(
        gsrn='gsrn2',
        subject='subject2',
    )

    # NOTE: Shares subject with DELEGATE_2
    DELEGATE_3 = DbMeteringPointDelegate(
        gsrn='gsrn3',
        subject='subject2',
    )

    @pytest.fixture(scope='function')
    def seeded_session(
            self,
            session: db.session
    ) -> db.Session:

        session.add(self.DELEGATE_1)
        session.add(self.DELEGATE_2)
        session.add(self.DELEGATE_3)
        session.commit()
        yield session

    def test__has_gsrn__single_gsrn_exists__should_return_correct_delegate(
            self,
            seeded_session: db.Session,
    ):
        # -- Act -----------------------------------------------------------------

        result = DelegateQuery(seeded_session) \
            .has_gsrn(self.DELEGATE_2.gsrn) \
            .all()

        # -- Assert --------------------------------------------------------------

        assert len(result) == 1
        assert result[0].gsrn == self.DELEGATE_2.gsrn

    @pytest.mark.parametrize('gsrn', ('unknown_gsrn_1', None))
    def test__has_gsrn__gsrn_does_not_exists__should_not_return_any_delegate(
            self,
            seeded_session: db.Session,
            gsrn: str,
    ):
        # -- Act -----------------------------------------------------------------

        result = DelegateQuery(seeded_session) \
            .has_gsrn(gsrn) \
            .all()

        # -- Assert --------------------------------------------------------------

        assert len(result) == 0

    def test__has_subject__single_subject_exists__should_return_correct_delegate(
            self,
            seeded_session: db.Session,
    ):
        # -- Act -----------------------------------------------------------------

        result = DelegateQuery(seeded_session) \
            .has_subject(self.DELEGATE_1.subject) \
            .all()

        # -- Assert --------------------------------------------------------------

        assert len(result) == 1
        assert result[0].subject == self.DELEGATE_1.subject

    def test__has_subject__multiple_subject_exists__should_return_correct_delegate(
            self,
            seeded_session: db.Session,
    ):
        # -- Act -----------------------------------------------------------------

        result = DelegateQuery(seeded_session) \
            .has_subject(self.DELEGATE_2.subject) \
            .all()

        # -- Assert --------------------------------------------------------------

        assert len(result) == 2
        assert all(delegate.subject == self.DELEGATE_2.subject for delegate in result)

    @pytest.mark.parametrize('subject', ('unknown_subject_1', None))
    def test__has_subject__subject_does_not_exists__should_not_return_any_delegate(
            self,
            seeded_session: db.Session,
            subject: str,
    ):
        # -- Act -----------------------------------------------------------------

        result = DelegateQuery(seeded_session) \
            .has_subject(subject) \
            .all()

        # -- Assert --------------------------------------------------------------

        assert len(result) == 0


class TestTechnologyQuery:
    # FIXME: Following tests fails when running with the other tests, but succeed when running alone
    # - test__has_fuel_code__multiple_exists__should_return_correct_technology
    # - test__has_fuel_code__single_exists__should_return_correct_technology
    TECHNOLOGY_1 = DbTechnology(
        tech_code='100',
        fuel_code='101',
    )

    TECHNOLOGY_2 = DbTechnology(
        tech_code='200',
        fuel_code='201',
    )

    # Shares codes with the others
    TECHNOLOGY_3 = DbTechnology(
        tech_code='100',
        fuel_code='201',
    )

    @pytest.fixture(scope='function')
    def seeded_session(
            self,
            session: db.session
    ) -> db.Session:
        session.add(self.TECHNOLOGY_1)
        session.add(self.TECHNOLOGY_2)
        session.add(self.TECHNOLOGY_3)
        session.commit()
        yield session

    def test__has_tech_code__single_exists__should_return_correct_technology(
            self,
            seeded_session: db.Session,
    ):

        # -- Act -----------------------------------------------------------------

        result = TechnologyQuery(seeded_session) \
            .has_tech_code(self.TECHNOLOGY_2.tech_code) \
            .all()

        # -- Assert --------------------------------------------------------------

        assert len(result) == 1
        assert result[0].tech_code == self.TECHNOLOGY_2.tech_code

    def test__has_tech_code__multiple_exists__should_return_correct_technology(
            self,
            seeded_session: db.Session,
    ):
        # -- Act -----------------------------------------------------------------

        result = TechnologyQuery(seeded_session) \
            .has_tech_code(self.TECHNOLOGY_3.tech_code) \
            .all()

        # -- Assert --------------------------------------------------------------

        assert len(result) > 0
        assert all(tech.tech_code == self.TECHNOLOGY_3.tech_code for tech in result)

    @pytest.mark.parametrize('tech_code', ('unknown_tech_code', None))
    def test__has_tech_code__does_not_exists__should_not_return_any_technology(
            self,
            seeded_session: db.Session,
            tech_code: str,
    ):
        # -- Act -----------------------------------------------------------------

        result = TechnologyQuery(seeded_session) \
            .has_tech_code(tech_code) \
            .all()

        # -- Assert --------------------------------------------------------------

        assert len(result) == 0

    def test__has_fuel_code__single_exists__should_return_correct_technology(
            self,
            seeded_session: db.Session,
    ):
        # -- Act -----------------------------------------------------------------

        result = TechnologyQuery(seeded_session) \
            .has_fuel_code(self.TECHNOLOGY_1.fuel_code) \
            .all()

        # -- Assert --------------------------------------------------------------

        assert len(result) == 1
        assert result[0].fuel_code == self.TECHNOLOGY_1.fuel_code

    def test__has_fuel_code__multiple_exists__should_return_correct_technology(
            self,
            seeded_session: db.Session,
    ):
        # -- Act -----------------------------------------------------------------

        result = TechnologyQuery(seeded_session) \
            .has_fuel_code(self.TECHNOLOGY_3.fuel_code) \
            .all()

        # -- Assert --------------------------------------------------------------

        assert len(result) > 0
        assert all(tech.fuel_code == self.TECHNOLOGY_3.fuel_code for tech in result)

    @pytest.mark.parametrize('fuel_code', ('unknown_fuel_code', None))
    def test__has_fuel_code__does_not_exists__should_not_return_any_technology(
            self,
            seeded_session: db.Session,
            fuel_code: str,
    ):
        # -- Act -----------------------------------------------------------------

        result = TechnologyQuery(seeded_session) \
            .has_fuel_code(fuel_code) \
            .all()

        # -- Assert --------------------------------------------------------------

        assert len(result) == 0
