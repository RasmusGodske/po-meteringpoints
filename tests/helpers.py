from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List
from flask.testing import FlaskClient


from energytt_platform.tokens import TokenEncoder

from energytt_platform.bus.messages.meteringpoints import \
    MeteringPointAddressUpdate, MeteringPointTechnologyUpdate

from energytt_platform.bus.messages.meteringpoints import MeteringPointUpdate
from energytt_platform.bus.messages.tech import TechnologyUpdate
from energytt_platform.bus.messages.delegates \
    import MeteringPointDelegateGranted

from energytt_platform.models.tech import \
    Technology, TechnologyCodes, TechnologyType
from energytt_platform.models.common import Address, EnergyDirection
from energytt_platform.models.meteringpoints import MeteringPoint
from energytt_platform.models.delegates import MeteringPointDelegate
from energytt_platform.models.auth import InternalToken

from meteringpoints_consumer.handlers import dispatcher

from meteringpoints_shared.db import db

METERPING_POINT_TYPES = [
    EnergyDirection.consumption,
    EnergyDirection.production,
]

TECH_CODES = ['100', '200', '300', '400']
FUEL_CODES = ['101', '201', '301', '401']

TECHNOLOGY_TYPES = [
    TechnologyType.coal,
    TechnologyType.solar,
    TechnologyType.wind,
    TechnologyType.nuclear,
]


def get_dummy_technology(number: int) -> Technology:
    """
    Returns dummy technology
    """
    technology_types_count = len(TECHNOLOGY_TYPES)
    tech_codes_count = len(TECH_CODES)
    fuel_codes_count = len(FUEL_CODES)

    return Technology(
        type=TECHNOLOGY_TYPES[number % technology_types_count],
        tech_code=TECH_CODES[number % tech_codes_count],
        fuel_code=FUEL_CODES[number % fuel_codes_count],
    )


def get_dummy_address(number: int) -> Address:
    """
    Returns dummy address
    """
    return Address(
        street_code='street_code#'+str(number),
        street_name='street_name#'+str(number),
        building_number='building_number#'+str(number),
        floor_id='floor_id#'+str(number),
        room_id='room_id#'+str(number),
        post_code='post_code#'+str(number),
        city_name='city_name#'+str(number),
        city_sub_division_name='city_sub_division_name#'+str(number),
        municipality_code='municipality_code#'+str(number),
        location_description='location_description#'+str(number),
    )


def get_dummy_meteringpoint(
        number: int,
        use_gsrn: str = None,
        include_technology: bool = False,
        include_address: bool = False
) -> MeteringPoint:
    """
    Returns dummy meteringpoint
    """
    meteringpoint_type_count = len(METERPING_POINT_TYPES)

    technology = get_dummy_technology(number) if include_technology else None
    address = get_dummy_address(number) if include_address else None

    # If no gsrn is specififed generate one
    gsrn = use_gsrn
    if use_gsrn is None:
        gsrn = 'GSRN'+str(number)

    return MeteringPoint(
        gsrn=gsrn,
        sector='DK'+str(number),
        type=METERPING_POINT_TYPES[number % meteringpoint_type_count],
        technology=technology,
        address=address
    )


def get_dummy_meteringpoint_list(
    count: int,
    use_gsrn: str = None,
    include_technology: bool = False,
    include_address: bool = False
) -> List[MeteringPoint]:
    """
    Returns a list of dummy meteringpoints
    """
    meteringpoint_list = []
    for x in range(count):
        meteringpoint = get_dummy_meteringpoint(
            number=x,
            use_gsrn=use_gsrn,
            include_technology=include_technology,
            include_address=include_address,
        )
        meteringpoint_list.append(meteringpoint)

    return meteringpoint_list


def get_dummy_token(
    token_encoder: TokenEncoder,
    subject: str,
    actor: str = 'foo',
    expired: bool = False,
    scopes: List[str] = None,
):
    """
    Returns a dummy token
    """
    issued = datetime.now(timezone.utc)
    expires = datetime.now(timezone.utc) + timedelta(hours=5)

    if expired:
        expires = datetime.now(timezone.utc) - timedelta(hours=5)

    internal_token = InternalToken(
        issued=issued,
        expires=expires,
        actor=actor,
        subject=subject,
        scope=scopes or [],
    )

    return token_encoder.encode(internal_token)


def get_all_technology_codes():
    for idx, (tech_code, fuel_code) in enumerate(zip(TECH_CODES, FUEL_CODES)):
        yield Technology(
            tech_code=tech_code,
            fuel_code=fuel_code,
            type=TECHNOLOGY_TYPES[idx % len(TECHNOLOGY_TYPES)]
        )


def insert_meteringpoint_and_delegate_access_to_subject(
    meteringpoint: MeteringPoint,
    token_subject: str
):
    # Insert metering point
    dispatcher(MeteringPointUpdate(
        meteringpoint=meteringpoint
    ))

    # Delegate access, needed to fetch it using api
    dispatcher(MeteringPointDelegateGranted(
        delegate=MeteringPointDelegate(
            subject=token_subject,
            gsrn=meteringpoint.gsrn,
        )
    ))


def make_dict_of_metering_point(mp: MeteringPoint) -> Dict[str, Any]:
    address = None
    technology = None

    if mp.address is not None:
        address = {
            'street_code': mp.address.street_code,
            'street_name': mp.address.street_name,
            'building_number': mp.address.building_number,
            'floor_id': mp.address.floor_id,
            'room_id': mp.address.room_id,
            'post_code': mp.address.post_code,
            'city_name': mp.address.city_name,
            'city_sub_division_name': mp.address.city_sub_division_name,
            'municipality_code': mp.address.municipality_code,
            'location_description': mp.address.location_description,
        }

    if mp.technology is not None:
        technology = {
            'fuel_code': mp.technology.fuel_code,
            'tech_code': mp.technology.tech_code,
            'type': mp.technology.type.value,
        }

    return {
        'gsrn': mp.gsrn,
        'type': mp.type.value,
        'sector': mp.sector,
        'technology': technology,
        'address': address
    }


def insert_technology_from_meteringpoint(meteringpoint: MeteringPoint):

    dispatcher(TechnologyUpdate(
        technology=meteringpoint.technology
    ))
