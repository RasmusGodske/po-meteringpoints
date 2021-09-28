from energytt_platform.bus import get_default_broker

from meteringpoints_shared.config import EVENT_BUS_SERVERS


broker = get_default_broker(
    group='meteringpoints',
    servers=EVENT_BUS_SERVERS,
)
