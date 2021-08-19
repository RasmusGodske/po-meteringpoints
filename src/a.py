from energytt_platform.bus import MessageSerializer, messages as m
from energytt_platform.models.meteringpoints import MeteringPoint, MeteringPointType

from meteringpoints_shared.db import db

m = m.MeteringPointAdded(
    meteringpoint=MeteringPoint(
        gsrn='1',
        type=MeteringPointType.production,
        sector='DK1',
    )
)

s = MessageSerializer()
x = s.deserialize(s.serialize(m))

j = 2
