"""
Runs a Message Bus consumer.
"""
from energytt_platform.bus import get_default_broker, topics as t

from meteringpoints_shared.config import EVENT_BUS_SERVERS

from .handlers import dispatcher


broker = get_default_broker(
    servers=EVENT_BUS_SERVERS,
)

broker.subscribe(
    topics=[t.METERINGPOINTS, t.TECHNOLOGIES],
    handler=dispatcher,
)
