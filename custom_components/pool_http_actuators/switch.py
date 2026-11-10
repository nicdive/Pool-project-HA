"""Switch platform — one switch per configured actuator."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import PoolHttpConfigEntry
from .const import (
    CONF_ACTUATOR_ID,
    CONF_ACTUATORS,
    CONF_HOST,
    CONF_OFF_PATH,
    CONF_ON_PATH,
    CONF_PORT,
    DEFAULT_PORT,
    DOMAIN,
)
from .http_client import PoolHttpClient, PoolHttpClientError

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: PoolHttpConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up switches from config entry options."""
    client = entry.runtime_data
    actuators = entry.options.get(CONF_ACTUATORS, [])
    async_add_entities(
        [
            PoolHttpActuatorSwitch(entry, client, actuator)
            for actuator in actuators
        ]
    )


class PoolHttpActuatorSwitch(SwitchEntity):
    """HTTP GET switch with optimistic state (no feedback from Arduino yet)."""

    _attr_should_poll = False
    _attr_has_entity_name = False

    def __init__(
        self,
        entry: PoolHttpConfigEntry,
        client: PoolHttpClient,
        actuator: dict[str, Any],
    ) -> None:
        self._client = client
        self._on_path: str = actuator[CONF_ON_PATH]
        self._off_path: str = actuator[CONF_OFF_PATH]
        self._actuator_id: str = actuator[CONF_ACTUATOR_ID]

        host = entry.data[CONF_HOST]
        port = entry.data.get(CONF_PORT, DEFAULT_PORT)

        self._attr_name = actuator["name"]
        self._attr_unique_id = f"{entry.entry_id}_{self._actuator_id}"
        self._attr_is_on = False
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{host}:{port}")},
            name=f"Pool HTTP ({host})",
            manufacturer="Arduino / HTTP relay",
            model="Web GET controller",
            configuration_url=client.base_url,
        )

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Send ON command (e.g. GET /ouvre)."""
        await self._async_send(self._on_path, True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Send OFF command (e.g. GET /ferme)."""
        await self._async_send(self._off_path, False)

    async def _async_send(self, path: str, assumed_on: bool) -> None:
        try:
            await self._client.async_send_command(path)
        except PoolHttpClientError as err:
            _LOGGER.error("Command failed for %s (%s): %s", self.name, path, err)
            raise HomeAssistantError(
                f"Impossible d'envoyer la commande « {path} » : {err}"
            ) from err

        # Optimistic: no status endpoint known until Arduino sketch is reviewed
        self._attr_is_on = assumed_on
        self.async_write_ha_state()
