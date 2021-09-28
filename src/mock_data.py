import uuid
from datetime import datetime, timedelta

from energytt_platform.bus import get_default_broker, messages as m, topics as t
from energytt_platform.models.common import Address
from energytt_platform.models.tech import \
    Technology, TechnologyCodes, TechnologyType
from energytt_platform.models.measurements import \
    Measurement, MeasurementType
from energytt_platform.models.meteringpoints import \
    MeteringPoint, MeteringPointType

from meteringpoints_shared.config import EVENT_BUS_SERVERS


# -- Technologies ------------------------------------------------------------

broker = get_default_broker(
    servers=EVENT_BUS_SERVERS,
)

broker.publish(
    topic=t.TECHNOLOGIES,
    msg=m.TechnologyUpdate(
        technology=Technology(
            tech_code='T010101',
            fuel_code='F01010101',
            type=TechnologyType.solar,
        ),
    ),
)

broker.publish(
    topic=t.TECHNOLOGIES,
    msg=m.TechnologyUpdate(
        technology=Technology(
            tech_code='T020202',
            fuel_code='F02020202',
            type=TechnologyType.wind,
        ),
    ),
)

broker.publish(
    topic=t.TECHNOLOGIES,
    msg=m.TechnologyUpdate(
        technology=Technology(
            tech_code='T030303',
            fuel_code='F03030303',
            type=TechnologyType.coal,
        ),
    ),
)


broker.publish(
    topic=t.TECHNOLOGIES,
    msg=m.MeteringPointTechnologyUpdate(
        gsrn='subject-80ecf905-d6b8-4a54-b437-653ee28e49ee-gsrn-1',
        codes=TechnologyCodes(
            tech_code='T030303',
            fuel_code='F03030303',
        ),
    ),
)


broker.publish(
    topic=t.TECHNOLOGIES,
    msg=m.MeteringPointAddressUpdate(
        gsrn='subject-80ecf905-d6b8-4a54-b437-653ee28e49ee-gsrn-2',
        address=Address(
            street_name='VEJNAVN!',
        ),
    ),
)





# broker.publish(
#     topic=t.METERINGPOINTS,
#     msg=m.UserOnboarded(
#         subject='3cb088c3-75dc-4020-9c81-9ac69f83e01f',
#         name='John Johnson',
#     ),
# )
