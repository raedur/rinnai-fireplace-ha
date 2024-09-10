"""Discovery for Rinnai Fireplace devices."""

from __future__ import annotations

import asyncio
import re
import time
from typing import TYPE_CHECKING, Optional

from attr import dataclass
from homeassistant.components import network
from scapy.all import AsyncSniffer, Packet
from scapy.layers.inet import UDP

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
TIMEOUT_SEC = 10
BROADCAST_PORT = 3500


@dataclass
class FoundDevice:
    id: str | None
    name: str
    ip: str


async def discover(hass: HomeAssistant) -> list[FoundDevice]:
    """Discover Rinnai Fireplace Devices."""
    adapters = await network.async_get_adapters(hass)
    ifaces = [
        adapt["name"]
        for adapt in adapters
        if adapt["enabled"] is True and len(adapt["ipv4"]) > 0
    ]

    if len(ifaces) == 0:
        return []

    devices = []
    # Record the start time
    start_time = time.time()

    # This function will return True when TIMEOUT_SEC seconds have elapsed
    def stop_filter(_: Packet) -> bool:
        return time.time() - start_time > TIMEOUT_SEC

    def process_packet(packet: Packet) -> FoundDevice | None:
        if UDP not in packet or packet[UDP].dport != BROADCAST_PORT:
            return None
        decoded = packet.load.decode()
        pattern = r".*RinnaiWiFi_(.{6})(.*)"
        result = re.search(pattern, decoded)
        if result is None:
            return None
        device_id = result.group(1)
        device_name = result.group(2)
        ip = packet[UDP].src
        devices.append(FoundDevice(device_id, device_name, ip))

    sniffer = AsyncSniffer(
        iface=ifaces,
        prn=process_packet,
        filter=f"udp and port {BROADCAST_PORT}",
        stop_filter=stop_filter,
    )
    sniffer.start()

    return devices
