import sqlalchemy as sa
from enum import Enum
from typing import List, Optional
from dataclasses import dataclass, field
from sqlalchemy.orm import relationship

from energytt_platform.serialize import Serializable
from energytt_platform.models.tech import TechnologyType
from energytt_platform.models.common import ResultOrdering
from energytt_platform.models.meteringpoints import MeteringPointType

from .db import db


# -- Common models -----------------------------------------------------------


@dataclass
class MeteringPointFilters(Serializable):
    """
    Filters for querying MeteringPoints.
    """
    gsrn: Optional[List[str]] = field(default=None)
    type: Optional[MeteringPointType] = field(default=None)
    sector: Optional[List[str]] = field(default=None)


class MeteringPointOrderingKeys(Enum):
    """
    Keys to order MeteringPoints by when querying.
    """
    gsrn = 'gsrn'
    type = 'type'
    sector = 'sector'


MeteringPointOrdering = ResultOrdering[MeteringPointOrderingKeys]


# -- Database models ---------------------------------------------------------


class DbMeteringPoint(db.ModelBase):
    """
    SQL representation of a MeteringPoint.
    """
    __tablename__ = 'meteringpoint'
    __table_args__ = (
        sa.PrimaryKeyConstraint('gsrn'),
        sa.UniqueConstraint('gsrn'),
    )

    gsrn = sa.Column(sa.String(), index=True, nullable=False)
    sector = sa.Column(sa.String(), index=True)
    type = sa.Column(sa.Enum(MeteringPointType), index=True)

    # -- Relationships -------------------------------------------------------

    address = relationship(
        'DbMeteringPointAddress',
        primaryjoin='foreign(DbMeteringPoint.gsrn) == DbMeteringPointAddress.gsrn',  # noqa: E501
        uselist=False,
        viewonly=True,
        lazy='joined',
    )

    # TODO Rewrite this?
    technology = relationship(
        'DbTechnology',
        primaryjoin='foreign(DbMeteringPoint.gsrn) == DbMeteringPointTechnology.gsrn',  # noqa: E501
        secondary='meteringpoint_technology',
        secondaryjoin=(
            'and_('
            'foreign(DbMeteringPointTechnology.tech_code) == DbTechnology.tech_code,'  # noqa: E501
            'foreign(DbMeteringPointTechnology.fuel_code) == DbTechnology.fuel_code'  # noqa: E501
            ')'
        ),
        uselist=False,
        viewonly=True,
        lazy='joined',
    )


class DbMeteringPointAddress(db.ModelBase):
    """
    SQL representation of a (physical) address for a MeteringPoint.
    """
    __tablename__ = 'meteringpoint_address'
    __table_args__ = (
        sa.PrimaryKeyConstraint('gsrn'),
        sa.UniqueConstraint('gsrn'),
    )

    gsrn = sa.Column(sa.String(), index=True, nullable=False)
    street_code = sa.Column(sa.String())
    street_name = sa.Column(sa.String())
    building_number = sa.Column(sa.String())
    floor_id = sa.Column(sa.String())
    room_id = sa.Column(sa.String())
    post_code = sa.Column(sa.String())
    city_name = sa.Column(sa.String())
    city_sub_division_name = sa.Column(sa.String())
    municipality_code = sa.Column(sa.String())
    location_description = sa.Column(sa.String())


class DbMeteringPointTechnology(db.ModelBase):
    """
    SQL representation of technology codes for a MeteringPoint.
    """
    __tablename__ = 'meteringpoint_technology'
    __table_args__ = (
        sa.PrimaryKeyConstraint('gsrn'),
        sa.UniqueConstraint('gsrn'),
    )

    gsrn = sa.Column(sa.String(), index=True, nullable=False)
    tech_code = sa.Column(sa.String())
    fuel_code = sa.Column(sa.String())


class DbMeteringPointDelegate(db.ModelBase):
    """
    TODO
    """
    __tablename__ = 'meteringpoint_delegate'
    __table_args__ = (
        sa.PrimaryKeyConstraint('gsrn', 'subject'),
    )

    gsrn = sa.Column(sa.String(), index=True, nullable=False)
    subject = sa.Column(sa.String())


class DbTechnology(db.ModelBase):
    """
    SQL representation of a Technology.
    """
    __tablename__ = 'technology'
    __table_args__ = (
        sa.PrimaryKeyConstraint('tech_code', 'fuel_code'),
        sa.UniqueConstraint('tech_code', 'fuel_code'),
    )

    fuel_code = sa.Column(sa.String())
    tech_code = sa.Column(sa.String())

    # TODO Use String instead of Enum (forward compatibility)
    type = sa.Column(sa.Enum(TechnologyType))
