"""Config flow for Xiaomi Humidifier 2."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_MODEL, CONF_NAME, CONF_TOKEN
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.device_registry import format_mac
from homeassistant.helpers.selector import SelectSelector, SelectSelectorConfig, TextSelector

from .const import CONF_MODEL_AUTO, DEFAULT_NAME, DOMAIN, MODE_LABELS, SUPPORTED_MODELS
from .device import (
    CannotConnectError,
    UnsupportedModelError,
    validate_input,
)


class XiaomiHumidifier2ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Xiaomi Humidifier 2."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""

        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                runtime_data = await self.hass.async_add_executor_job(validate_input, user_input)
            except CannotConnectError:
                errors["base"] = "cannot_connect"
            except UnsupportedModelError:
                errors["base"] = "unsupported_model"
            except Exception:
                errors["base"] = "unknown"
            else:
                unique_id = format_mac(runtime_data.info.mac_address or "")
                await self.async_set_unique_id(unique_id or f"{runtime_data.model}-{user_input[CONF_HOST]}")
                self._abort_if_unique_id_configured()

                title = user_input.get(CONF_NAME) or runtime_data.info.model or DEFAULT_NAME
                data = {
                    CONF_HOST: user_input[CONF_HOST],
                    CONF_TOKEN: user_input[CONF_TOKEN],
                    CONF_MODEL: runtime_data.model,
                    CONF_NAME: user_input.get(CONF_NAME) or title,
                }
                return self.async_create_entry(
                    title=title,
                    data=data,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): TextSelector(),
                    vol.Required(CONF_TOKEN): TextSelector(),
                    vol.Required(CONF_MODEL, default=CONF_MODEL_AUTO): SelectSelector(
                        SelectSelectorConfig(
                            options=[
                                {"label": MODE_LABELS[model], "value": model}
                                for model in (CONF_MODEL_AUTO, *SUPPORTED_MODELS)
                            ]
                        )
                    ),
                    vol.Optional(CONF_NAME, default=DEFAULT_NAME): TextSelector(),
                }
            ),
            errors=errors,
        )
