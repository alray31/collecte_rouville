"""Collecte Rouville — intégration HACS pour les collectes municipales Publidata."""
from __future__ import annotations

import logging
from datetime import timedelta

import aiohttp
from icalendar import Calendar

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_ICS_URL, DOMAIN, SCAN_INTERVAL_HOURS

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})
    coordinator = CollecteCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


class CollecteCoordinator(DataUpdateCoordinator):
    """Récupère et parse le fichier ICS toutes les SCAN_INTERVAL_HOURS heures."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=SCAN_INTERVAL_HOURS),
        )
        self.ics_url: str = entry.data[CONF_ICS_URL]
        self.ville: str = entry.data.get("ville", "")
        self._session = async_get_clientsession(hass)

    async def _async_update_data(self) -> dict:
        try:
            async with self._session.get(
                self.ics_url, timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                resp.raise_for_status()
                raw = await resp.read()
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Erreur réseau : {err}") from err

        try:
            cal = Calendar.from_ical(raw)
        except Exception as err:
            raise UpdateFailed(f"Erreur parsing ICS : {err}") from err

        from .parser import parse_collecte_events
        return parse_collecte_events(cal)
