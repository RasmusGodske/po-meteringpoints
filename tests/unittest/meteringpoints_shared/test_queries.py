import pytest
from typing import List
from itertools import product

from energytt_platform.models.common import Order
from energytt_platform.models.meteringpoints import (
    MeteringPoint,
    MeteringPointType,
)

from meteringpoints_shared.db import db
from meteringpoints_shared.models import (
    DbMeteringPoint,
    DbMeteringPointAddress,
    DbMeteringPointTechnology,
    DbMeteringPointDelegate,
    DbTechnology,
    MeteringPointFilters,
    MeteringPointOrdering,
    MeteringPointOrderingKeys,
)
from meteringpoints_shared.queries import (
    MeteringPointQuery,
    MeteringPointAddressQuery,
    MeteringPointTechnologyQuery,
    DelegateQuery,
    TechnologyQuery,
)


class TestMeteringPointQuery:
    """
    Tests MeteringPointQuery.
    """

    @pytest.fixture(scope='function')
    def seed_meteringpoints(self) -> List[MeteringPoint]:
        """
        Returns a list of MeteringPoints to seed the database with before
        before running tests.
        """
        types = (MeteringPointType.consumption, MeteringPointType.production)
        sectors = ('DK1', 'DK2')
        combinations = product(types, sectors)

        meteringpoints = []

        for i, (type, sector) in enumerate(combinations):
            meteringpoints.append(DbMeteringPoint(
                gsrn=f'gsrn{i}',
                type=type,
                sector=sector,
            ))

        return meteringpoints

    @pytest.fixture(scope='function', autouse=True)
    def setup(
            self,
            session: db.Session,
            seed_meteringpoints: List[MeteringPoint],
    ):
        """
        Seeds the database with MeteringPoints before running tests.

        :param session: Database session
        :param seed_meteringpoints: MeteringPoints to seed database with
        """
        session.begin()

        for meteringpoint in seed_meteringpoints:
            session.add(DbMeteringPoint(
                gsrn=meteringpoint.gsrn,
                type=meteringpoint.type,
                sector=meteringpoint.sector,
            ))

        session.commit()

    @pytest.mark.parametrize('gsrn', ('gsrn0', 'gsrn1', 'gsrn2'))
    def test__has_gsrn__meteringpoint_exists__should_return_correct_meteringpoint(  # noqa: E501
            self,
            session: db.Session,
            gsrn: str,
    ):
        """
        :param session: Database session
        :param gsrn: GSRN to fetch from database (expected to exist)
        """

        # -- Act -------------------------------------------------------------

        query = MeteringPointQuery(session) \
            .has_gsrn(gsrn)

        # -- Assert ----------------------------------------------------------

        assert query.count() == 1
        assert query.one().gsrn == gsrn

    @pytest.mark.parametrize('gsrn', ('unknown_gsrn_1', None))
    def test__has_gsrn__meteringpoint_does_not_exist__should_return_no_meteringpoints(  # noqa: E501
            self,
            session: db.Session,
            gsrn: str,
    ):
        """
        :param session: Database session
        :param gsrn: GSRN to fetch from database (expected NOT to exist)
        """

        assert not MeteringPointQuery(session) \
            .has_gsrn(gsrn) \
            .exists()

    @pytest.mark.parametrize('gsrn, expected_gsrn_returned', (
        (['gsrn0'], ['gsrn0']),
        (['gsrn0', 'gsrn1'], ['gsrn0', 'gsrn1']),
        (['unknown_gsrn_1'], []),
        (['unknown_gsrn_1', 'gsrn1'], ['gsrn1']),
        ([], []),
    ))
    def test__has_any_gsrn__should_return_correct_meteringpoints(
            self,
            session: db.Session,
            gsrn: List[str],
            expected_gsrn_returned: List[str],
    ):
        """
        :param session: Database session
        :param gsrn: GSRN numbers to fetch from database
        :param expected_gsrn_returned: GSRN number to expect returned
        """

        # -- Act -------------------------------------------------------------

        query = MeteringPointQuery(session) \
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
            session: db.Session,
            meteringpoint_type: MeteringPointType,
    ):
        """
        :param session: Database session
        :param meteringpoint_type: MeteringPoint type to select
        """

        # -- Act -------------------------------------------------------------

        results = MeteringPointQuery(session) \
            .is_type(meteringpoint_type) \
            .all()

        # -- Assert ----------------------------------------------------------

        assert len(results) > 0
        assert all(mp.type is meteringpoint_type for mp in results)

    @pytest.mark.parametrize('sector', ('DK1', 'DK2'))
    def test__in_sector__sector_exists__should_return_correct_meteringpoints(
            self,
            session: db.Session,
            seed_meteringpoints: List[MeteringPoint],
            sector: str,
    ):
        """
        :param session: Database session
        :param seed_meteringpoints: All seeded MeteringPoints
        :param sector: Sector to select
        """

        # -- Act - -----------------------------------------------------------

        results = MeteringPointQuery(session) \
            .in_sector(sector) \
            .all()

        # -- Assert ----------------------------------------------------------

        expected_meteringpoints = \
            [mp for mp in seed_meteringpoints if mp.sector == sector]

        assert len(results) > 0
        assert len(results) == len(expected_meteringpoints)
        assert all(mp.sector == sector for mp in results)

    @pytest.mark.parametrize('sector', ('', 'unknown_sector', None))
    def test__in_sector__sector_does_not_exist__should_return_nothing(
            self,
            session: db.Session,
            seed_meteringpoints: List[MeteringPoint],
            sector: str,
    ):
        """
        :param session: Database session
        :param seed_meteringpoints: All seeded MeteringPoints
        :param sector: Sector to select
        """

        assert not MeteringPointQuery(session) \
            .in_sector(sector) \
            .exists()

    @pytest.mark.parametrize('sectors', (
        [],
        [''],
        [None],
        ['DK1'],
        ['DK1', 'DK2'],
        ['unknown_sector'],
        ['DK1', 'unknown_sector'],
        ['DK1', 'DK1'],
    ))
    def test__in_any_sector__should_return_correct_meteringpoints(
            self,
            session: db.Session,
            seed_meteringpoints: List[MeteringPoint],
            sectors: List[str],
    ):
        """
        :param session: Database session
        :param seed_meteringpoints: All seeded MeteringPoints
        :param sectors: Sectors to select
        """

        # -- Act -------------------------------------------------------------

        results = MeteringPointQuery(session) \
            .in_any_sector(sectors) \
            .all()

        # -- Assert ----------------------------------------------------------

        expected_meteringpoints = \
            [mp for mp in seed_meteringpoints if mp.sector in sectors]

        assert len(results) == len(expected_meteringpoints)
        assert all(mp.sector in sectors for mp in results)

    def test__is_accessible_by__should_return_meteringpoints_with_delegated_access(  # noqa: E501
            self,
            session: db.Session,
    ):
        """
        :param session: Database session
        """

        # -- Arrange ---------------------------------------------------------

        session.begin()
        session.add(DbMeteringPointDelegate(gsrn='gsrn1', subject='subject1'))
        session.add(DbMeteringPointDelegate(gsrn='gsrn2', subject='subject1'))
        session.commit()

        # -- Act -------------------------------------------------------------

        results = MeteringPointQuery(session) \
            .is_accessible_by('subject1') \
            .all()

        # -- Assert ----------------------------------------------------------

        assert len(results) == 2
        assert all(mp.gsrn in ('gsrn1', 'gsrn2') for mp in results)

    @pytest.mark.parametrize('filters', (
        MeteringPointFilters(gsrn=['gsrn1', 'gsrn2']),
        MeteringPointFilters(sector=['DK1']),
        MeteringPointFilters(type=MeteringPointType.production),
        MeteringPointFilters(
            gsrn=['gsrn1'],
            sector=['DK2'],
            type=MeteringPointType.consumption,
        ),
    ))
    def test__apply_filters__meteringpoints_exists__should_return_correct_meteringpoints(  # noqa: E501
            self,
            session: db.Session,
            filters: MeteringPointFilters,
    ):
        """
        :param session: Database session
        :param filters: Filter to apply to query
        """

        # -- Act -------------------------------------------------------------

        results = MeteringPointQuery(session) \
            .apply_filters(filters) \
            .all()

        # -- Assert ----------------------------------------------------------

        assert len(results) > 0

        if filters.gsrn is not None:
            assert all(mp.gsrn in filters.gsrn for mp in results)

        if filters.type is not None:
            assert all(mp.type is filters.type for mp in results)

        if filters.sector is not None:
            assert all(mp.sector in filters.sector for mp in results)

    @pytest.mark.parametrize('filters', (
        MeteringPointFilters(gsrn=['foo', 'bar']),
        MeteringPointFilters(sector=['spam']),
        MeteringPointFilters(gsrn=['foobar'], sector=['DK2']),
        MeteringPointFilters(gsrn=['gsrn1'], sector=['foobar']),
    ))
    def test__query_apply_filters__meteringpoints_does_not_exist__should_return_no_meteringpoints(  # noqa: E501
            self,
            session: db.Session,
            filters: MeteringPointFilters,
    ):
        """
        :param session: Database session
        :param filters: Filter to apply to query
        """

        assert not MeteringPointQuery(session) \
            .apply_filters(filters) \
            .exists()

    @pytest.mark.parametrize('ordering', (
        MeteringPointOrdering(
            key=MeteringPointOrderingKeys.gsrn,
            order=Order.asc,
        ),
        MeteringPointOrdering(
            key=MeteringPointOrderingKeys.gsrn,
            order=Order.desc,
        ),
        MeteringPointOrdering(
            key=MeteringPointOrderingKeys.sector,
            order=Order.asc,
        ),
        MeteringPointOrdering(
            key=MeteringPointOrderingKeys.sector,
            order=Order.desc,
        ),
    ))
    def test__apply_ordering__should_return_correct_meteringpoints(
            self,
            session: db.Session,
            ordering: MeteringPointOrdering,
            seed_meteringpoints: List[MeteringPoint],
    ):
        """
        :param session: Database session
        :param ordering: Ordering to apply to query
        """

        # -- Act -------------------------------------------------------------

        results = MeteringPointQuery(session) \
            .apply_ordering(ordering) \
            .all()

        # -- Assert ----------------------------------------------------------

        sort_descending = ordering.order == Order.desc

        if ordering.key is MeteringPointOrderingKeys.gsrn:
            f = lambda mp: mp.gsrn  # noqa: E731
        elif ordering.key is MeteringPointOrderingKeys.sector:
            f = lambda mp: mp.sector  # noqa: E731
        else:
            raise RuntimeError('Should not happen')

        gsrn_expected = [mp.gsrn for mp in sorted(
            seed_meteringpoints, key=f, reverse=sort_descending)]

        assert len(results) == len(seed_meteringpoints)
        assert [mp.gsrn for mp in results] == gsrn_expected


class TestMeteringPointAddressQuery:
    """
    Tests MeteringPointAddressQuery.
    """

    def test__has_gsrn__address_exists__should_return_correct_address(
            self,
            session: db.Session,
    ):
        """
        :param session: Database session
        """

        # -- Arrange ---------------------------------------------------------

        session.begin()
        session.add(DbMeteringPointAddress(gsrn='gsrn1'))
        session.add(DbMeteringPointAddress(gsrn='gsrn2'))
        session.commit()

        # -- Assert ----------------------------------------------------------

        address = MeteringPointAddressQuery(session) \
            .has_gsrn('gsrn1') \
            .one()

        # -- Assert ----------------------------------------------------------

        assert address.gsrn == 'gsrn1'

    @pytest.mark.parametrize('gsrn', ('', None, 'unknown_gsrn_1'))
    def test__has_gsrn__address_does_not_exists__should_not_return_anything(
            self,
            session: db.Session,
            gsrn: str,
    ):
        """
        :param session: Database session
        :param gsrn: GSRN to select
        """

        assert not MeteringPointAddressQuery(session) \
            .has_gsrn(gsrn) \
            .exists()


class TestMeteringPointTechnologyQuery:
    """
    Tests MeteringPointTechnologyQuery.
    """

    def test__has_gsrn__technology_exists__should_return_correct_technology(
            self,
            session: db.Session,
    ):
        """
        :param session: Database session
        """

        # -- Arrange ---------------------------------------------------------

        session.begin()

        session.add(DbMeteringPointTechnology(
            gsrn='gsrn1',
            tech_code='T010101',
            fuel_code='F01010101',
        ))

        session.add(DbMeteringPointTechnology(
            gsrn='gsrn2',
            tech_code='T020202',
            fuel_code='F02020202',
        ))

        session.commit()

        # -- Assert ----------------------------------------------------------

        technology = MeteringPointTechnologyQuery(session) \
            .has_gsrn('gsrn1') \
            .one()

        # -- Assert ----------------------------------------------------------

        assert technology.gsrn == 'gsrn1'

    @pytest.mark.parametrize('gsrn', ('', None, 'unknown_gsrn_1'))
    def test__has_gsrn__gsrn_does_not_exists__should_not_return_anything(
            self,
            session: db.Session,
            gsrn: str,
    ):
        """
        :param session: Database session
        :param gsrn: GSRN to select
        """

        assert not MeteringPointTechnologyQuery(session) \
            .has_gsrn(gsrn) \
            .exists()


class TestDelegateQuery:
    """
    Tests DelegateQuery.
    """

    @pytest.fixture(scope='function', autouse=True)
    def setup(
            self,
            session: db.session
    ):
        """
        Seeds the database with MeteringPointDelegates before running tests.

        :param session: Database session
        """
        session.begin()
        session.add(DbMeteringPointDelegate(gsrn='gsrn1', subject='subject1'))
        session.add(DbMeteringPointDelegate(gsrn='gsrn1', subject='subject2'))
        session.add(DbMeteringPointDelegate(gsrn='gsrn2', subject='subject1'))
        session.add(DbMeteringPointDelegate(gsrn='gsrn2', subject='subject2'))
        session.commit()

    def test__has_gsrn__delegates_exists__should_return_correct_delegates(
            self,
            session: db.Session,
    ):
        """
        :param session: Database session
        """

        # -- Assert ----------------------------------------------------------

        delegates = DelegateQuery(session) \
            .has_gsrn('gsrn1') \
            .all()

        # -- Assert ----------------------------------------------------------

        assert len(delegates) == 2
        assert all(delegate.gsrn == 'gsrn1' for delegate in delegates)

    @pytest.mark.parametrize('gsrn', ('', None, 'unknown_gsrn'))
    def test__has_gsrn__delegate_does_not_exist__should_not_return_anything(
            self,
            session: db.Session,
            gsrn: str,
    ):
        """
        :param session: Database session
        :param gsrn: GSRN to select
        """

        assert not DelegateQuery(session) \
            .has_gsrn(gsrn) \
            .exists()

    def test__has_subject__delegates_exists__should_return_correct_delegates(
            self,
            session: db.Session,
    ):
        """
        :param session: Database session
        """

        # -- Assert ----------------------------------------------------------

        delegates = DelegateQuery(session) \
            .has_subject('subject1') \
            .all()

        # -- Assert ----------------------------------------------------------

        assert len(delegates) == 2
        assert all(delegate.subject == 'subject1' for delegate in delegates)

    @pytest.mark.parametrize('subject', ('', None, 'unknown_subject'))
    def test__has_subject__delegate_does_not_exist__should_not_return_anything(  # noqa: E501
            self,
            session: db.Session,
            subject: str,
    ):
        """
        :param session: Database session
        :param subject: Subject to select
        """

        assert not DelegateQuery(session) \
            .has_subject(subject) \
            .exists()


class TestTechnologyQuery:
    """
    Tests TechnologyQuery.
    """

    @pytest.fixture(scope='function', autouse=True)
    def setup(
            self,
            session: db.session
    ):
        """
        Seeds the database with Technologies before running tests.

        :param session: Database session
        """
        session.begin()
        session.add(DbTechnology(tech_code='T010101', fuel_code='F01010101'))
        session.add(DbTechnology(tech_code='T010101', fuel_code='F02020202'))
        session.add(DbTechnology(tech_code='T020202', fuel_code='F01010101'))
        session.add(DbTechnology(tech_code='T020202', fuel_code='F02020202'))
        session.commit()

    def test__has_tech_code__technology_exists__should_return_correct_technologies(  # noqa: E501
            self,
            session: db.Session,
    ):
        """
        :param session: Database session
        """

        # -- Act -------------------------------------------------------------

        results = TechnologyQuery(session) \
            .has_tech_code('T010101') \
            .all()

        # -- Assert ----------------------------------------------------------

        assert len(results) == 2
        assert all(tech.tech_code == 'T010101' for tech in results)

    @pytest.mark.parametrize('tech_code', ('', None, 'unknown_tech_code'))
    def test__has_tech_code__technology_does_not_exists__should_not_return_anything(  # noqa: E501
            self,
            session: db.Session,
            tech_code: str,
    ):
        """
        :param session: Database session
        """

        assert not TechnologyQuery(session) \
            .has_tech_code(tech_code) \
            .exists()

    def test__has_fuel_code__technology_exists__should_return_correct_technologies(  # noqa: E501
            self,
            session: db.Session,
    ):
        """
        :param session: Database session
        """

        # -- Act -------------------------------------------------------------

        results = TechnologyQuery(session) \
            .has_fuel_code('F01010101') \
            .all()

        # -- Assert ----------------------------------------------------------

        assert len(results) == 2
        assert all(tech.fuel_code == 'F01010101' for tech in results)

    @pytest.mark.parametrize('fuel_code', ('', None, 'unknown_fuel_code'))
    def test__has_fuel_code__technology_does_not_exists__should_not_return_anything(  # noqa: E501
            self,
            session: db.Session,
            fuel_code: str,
    ):
        """
        :param session: Database session
        """

        assert not TechnologyQuery(session) \
            .has_fuel_code(fuel_code) \
            .exists()
