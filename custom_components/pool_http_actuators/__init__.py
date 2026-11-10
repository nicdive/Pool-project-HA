"""Pool HTTP Actuators — control Arduino/web-relay devices via HTTP GET."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_HOST, CONF_PORT, DEFAULT_PORT, DOMAIN
from .http_client import PoolHttpClient

PLATFORMS: list[Platform] = [Platform.SWITCH]

type PoolHttpConfigEntry = ConfigEntry[PoolHttpClient]


async def async_setup_entry(hass: HomeAssistant, entry: PoolHttpConfigEntry) -> bool:
    """Set up Pool HTTP Actuators from a config entry."""
    host: str = entry.data[CONF_HOST]
    port: int = entry.data.get(CONF_PORT, DEFAULT_PORT)
    session = async_get_clientsession(hass)
    entry.runtime_data = PoolHttpClient(session, host, port)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: PoolHttpConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload when options (actuator list) change."""
    await hass.config_entries.async_reload(entry.entry_id)
