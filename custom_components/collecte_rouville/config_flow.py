"""Config flow pour Collecte Rouville — sélection de ville."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol
from icalendar import Calendar

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_ICS_URL, CONF_VILLE, DOMAIN, VILLES, VILLES_LIST

_LOGGER = logging.getLogger(__name__)


def _build_schema() -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(CONF_VILLE): vol.In(VILLES_LIST),
        }
    )


async def _validate_ics(session: aiohttp.ClientSession, url: str) -> str | None:
    """Retourne None si OK, sinon un code d'erreur."""
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=20)) as resp:
            if resp.status != 200:
                return "cannot_connect"
            raw = await resp.read()
    except aiohttp.ClientError:
        return "cannot_connect"
    try:
        cal = Calendar.from_ical(raw)
        events = [c for c in cal.walk() if c.name == "VEVENT"]
        if not events:
            return "empty_calendar"
    except Exception:
        return "invalid_ics"
    return None


class CollecteConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the config flow for Collecte Rouville."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            ville = user_input[CONF_VILLE]
            ics_url = VILLES[ville]["ics_url"]

            session = async_get_clientsession(self.hass)
            error = await _validate_ics(session, ics_url)

            if error:
                errors["base"] = error
            else:
                ville_id = ville.lower().replace(" ", "_").replace("-", "_").replace("'", "_")
                await self.async_set_unique_id(f"collecte_{ville_id}")
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"Collecte – {ville}",
                    data={
                        CONF_VILLE: ville,
                        CONF_ICS_URL: ics_url,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=_build_schema(),
            errors=errors,
        )
