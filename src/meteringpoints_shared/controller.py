from typing import Union

from energytt_platform.models.common import Address
from energytt_platform.models.tech import Technology, TechnologyCodes

from meteringpoints_shared.db import db
from meteringpoints_shared.models import (
    DbMeteringPoint,
    DbMeteringPointAddress,
    DbMeteringPointTechnology,
    DbMeteringPointDelegate,
    DbTechnology,
)
from meteringpoints_shared.queries import (
    MeteringPointQuery,
    MeteringPointAddressQuery,
    MeteringPointTechnologyQuery,
    DelegateQuery,
    TechnologyQuery,
)


TAddress = Union[
    Address,
    DbMeteringPointAddress,
]

TTechnology = Union[
    Technology,
    TechnologyCodes,
    DbTechnology,
    DbMeteringPointTechnology,
]


class DatabaseController(object):
    """
    Controls business logic for SQL database.
    """

    # -- MeteringPoints ------------------------------------------------------

    def get_or_create_meteringpoint(
            self,
            session: db.Session,
            gsrn: str,
    ) -> DbMeteringPoint:
        """
        Gets DbMeteringPoint from database, or creates a new if not found.
        """
        meteringpoint = MeteringPointQuery(session) \
            .has_gsrn(gsrn) \
            .one_or_none()

        if meteringpoint is None:
            meteringpoint = DbMeteringPoint(gsrn=gsrn)
            session.add(meteringpoint)

        return meteringpoint

    def delete_meteringpoint(
            self,
            session: db.Session,
            gsrn: str,
    ):
        """
        Delete a DbMeteringPoint and all of its associated data.
        """
        MeteringPointQuery(session) \
            .has_gsrn(gsrn) \
            .delete()

        MeteringPointAddressQuery(session) \
            .has_gsrn(gsrn) \
            .delete()

        MeteringPointTechnologyQuery(session) \
            .has_gsrn(gsrn) \
            .delete()

        DelegateQuery(session) \
            .has_gsrn(gsrn) \
            .delete()

    # -- MeteringPoint Addresses ---------------------------------------------

    def set_meteringpoint_address(
            self,
            session: db.Session,
            gsrn: str,
            address: TAddress,
    ):
        """
        Creates or updates address for a DbMeteringPoint.
        """
        meteringpoint_address = MeteringPointAddressQuery(session) \
            .has_gsrn(gsrn) \
            .one_or_none()

        if meteringpoint_address is None:
            meteringpoint_address = DbMeteringPointAddress(gsrn=gsrn)
            session.add(meteringpoint_address)

        meteringpoint_address.street_code = address.street_code
        meteringpoint_address.street_name = address.street_name
        meteringpoint_address.building_number = address.building_number
        meteringpoint_address.floor_id = address.floor_id
        meteringpoint_address.room_id = address.room_id
        meteringpoint_address.post_code = address.post_code
        meteringpoint_address.city_name = address.city_name
        meteringpoint_address.city_sub_division_name = address.city_sub_division_name
        meteringpoint_address.municipality_code = address.municipality_code
        meteringpoint_address.location_description = address.location_description

    def delete_meteringpoint_address(
            self,
            session: db.Session,
            gsrn: str,
    ):
        """
        TODO
        """
        MeteringPointAddressQuery(session) \
            .has_gsrn(gsrn) \
            .delete()

    # -- MeteringPoint Delegates ---------------------------------------------

    def grant_meteringpoint_delegate(
            self,
            session: db.Session,
            gsrn: str,
            subject: str,
    ):
        """
        Grant subject access to DbMeteringPoint with gsrn.
        """
        exists = DelegateQuery(session) \
            .has_gsrn(gsrn) \
            .has_subject(subject) \
            .exists()

        if not exists:
            session.add(DbMeteringPointDelegate(
                gsrn=gsrn,
                subject=subject,
            ))

    def revoke_meteringpoint_delegate(
            self,
            session: db.Session,
            gsrn: str,
            subject: str,
    ):
        """
        TODO
        """
        DelegateQuery(session) \
            .has_gsrn(gsrn) \
            .has_subject(subject) \
            .delete()

    # -- MeteringPoint Technologies ------------------------------------------

    def set_meteringpoint_technology(
            self,
            session: db.Session,
            gsrn: str,
            technology: TTechnology,
    ):
        """
        TODO
        """
        meteringpoint_technology = MeteringPointTechnologyQuery(session) \
            .has_gsrn(gsrn) \
            .one_or_none()

        if meteringpoint_technology is None:
            meteringpoint_technology = DbMeteringPointTechnology(gsrn=gsrn)
            session.add(meteringpoint_technology)

        meteringpoint_technology.tech_code = technology.tech_code
        meteringpoint_technology.fuel_code = technology.fuel_code

    def delete_meteringpoint_technology(
            self,
            session: db.Session,
            gsrn: str,
    ):
        """
        TODO
        """
        MeteringPointTechnologyQuery(session) \
            .has_gsrn(gsrn) \
            .delete()

    # -- Technologies --------------------------------------------------------

    def get_or_create_technology(
            self,
            session: db.Session,
            tech_code: str,
            fuel_code: str,
    ) -> DbTechnology:
        """
        TODO
        """
        technology = TechnologyQuery(session) \
            .has_tech_code(tech_code) \
            .has_fuel_code(fuel_code) \
            .one_or_none()

        if technology is None:
            technology = DbTechnology(tech_code=tech_code, fuel_code=fuel_code)
            session.add(technology)

        return technology

    def delete_technology(
            self,
            session: db.Session,
            tech_code: str,
            fuel_code: str,
    ):
        """
        TODO
        """
        TechnologyQuery(session) \
            .has_tech_code(tech_code) \
            .has_fuel_code(fuel_code) \
            .delete()


# -- Singletons --------------------------------------------------------------


controller = DatabaseController()
