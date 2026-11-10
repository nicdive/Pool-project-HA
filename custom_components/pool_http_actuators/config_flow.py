"""Config flow for Pool HTTP Actuators."""

from __future__ import annotations

from typing import Any
import uuid

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_ACTUATOR_ID,
    CONF_ACTUATORS,
    CONF_HOST,
    CONF_OFF_PATH,
    CONF_ON_PATH,
    CONF_PORT,
    DEFAULT_PORT,
    DOMAIN,
    STEP_ADD,
    STEP_REMOVE,
)
from .http_client import PoolHttpClient

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): selector.TextSelector(
            selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
        ),
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=1,
                max=65535,
                mode=selector.NumberSelectorMode.BOX,
            )
        ),
    }
)


class PoolHttpActuatorsConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle initial setup: one config entry per controller IP."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Ask for controller IP (and optional port)."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = str(user_input[CONF_HOST]).strip()
            port = int(user_input.get(CONF_PORT, DEFAULT_PORT))

            await self.async_set_unique_id(f"{host}:{port}")
            self._abort_if_unique_id_configured()

            session = async_get_clientsession(self.hass)
            client = PoolHttpClient(session, host, port)
            if not await client.async_test_connection():
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title=f"Pool HTTP ({host})",
                    data={CONF_HOST: host, CONF_PORT: port},
                    options={CONF_ACTUATORS: []},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Return the options flow to add/remove actuators."""
        return PoolHttpActuatorsOptionsFlow()


class PoolHttpActuatorsOptionsFlow(OptionsFlow):
    """Add or remove switches (open/close GET paths) on a controller."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Menu: add device or remove device."""
        actuators = list(self.config_entry.options.get(CONF_ACTUATORS, []))

        return self.async_show_menu(
            step_id="init",
            menu_options=[STEP_ADD]
            + ([STEP_REMOVE] if actuators else []),
        )

    async def async_step_add(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Add an actuator with on/off command strings."""
        errors: dict[str, str] = {}

        if user_input is not None:
            name = str(user_input["name"]).strip()
            on_path = str(user_input[CONF_ON_PATH]).strip().lstrip("/")
            off_path = str(user_input[CONF_OFF_PATH]).strip().lstrip("/")

            if not name or not on_path or not off_path:
                errors["base"] = "invalid_paths"
            else:
                actuators = list(self.config_entry.options.get(CONF_ACTUATORS, []))
                actuators.append(
                    {
                        CONF_ACTUATOR_ID: uuid.uuid4().hex,
                        "name": name,
                        CONF_ON_PATH: on_path,
                        CONF_OFF_PATH: off_path,
                    }
                )
                return self.async_create_entry(
                    title="",
                    data={CONF_ACTUATORS: actuators},
                )

        schema = vol.Schema(
            {
                vol.Required("name"): selector.TextSelector(),
                vol.Required(CONF_ON_PATH, default="ouvre"): selector.TextSelector(),
                vol.Required(CONF_OFF_PATH, default="ferme"): selector.TextSelector(),
            }
        )
        return self.async_show_form(
            step_id=STEP_ADD,
            data_schema=schema,
            errors=errors,
            description_placeholders={
                "example_on": "ouvre",
                "example_off": "ferme",
                "example_url": "http://192.168.23.241/ouvre",
            },
        )

    async def async_step_remove(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Remove one or more actuators."""
        actuators = list(self.config_entry.options.get(CONF_ACTUATORS, []))
        choices = {
            item[CONF_ACTUATOR_ID]: item["name"] for item in actuators
        }

        if user_input is not None:
            to_remove = set(user_input.get("actuators_to_remove", []))
            remaining = [
                item
                for item in actuators
                if item[CONF_ACTUATOR_ID] not in to_remove
            ]
            return self.async_create_entry(
                title="",
                data={CONF_ACTUATORS: remaining},
            )

        schema = vol.Schema(
            {
                vol.Required("actuators_to_remove"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            selector.SelectOptionDict(value=aid, label=label)
                            for aid, label in choices.items()
                        ],
                        multiple=True,
                        mode=selector.SelectSelectorMode.LIST,
                    )
                )
            }
        )
        return self.async_show_form(step_id=STEP_REMOVE, data_schema=schema)
