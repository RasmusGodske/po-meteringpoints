from energytt_platform.bus import get_default_broker

from meteringpoints_shared.config import MESSAGE_BUS_SERVERS


broker = get_default_broker(
    group='meteringpoints',
    servers=MESSAGE_BUS_SERVERS,
)
