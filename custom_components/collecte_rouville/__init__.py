"""Collecte MRC de Rouville - v3.0 (API REST Publidata)."""

from __future__ import annotations

import logging
from datetime import date, timedelta

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    API_INSTANCE_ID,
    API_SEARCH_URL,
    COLLECTE_TYPES,
    CONF_ADDRESS_ID,
    CONF_LAT,
    CONF_LON,
    DOMAIN,
    SCAN_INTERVAL_HOURS,
)
from .schedule_parser import dates_futures, prochaine_date

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "binary_sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    coordinator = CollecteRouvilleCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


class CollecteRouvilleCoordinator(DataUpdateCoordinator):
    """Coordinator qui récupère les données via l'API REST Publidata."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=SCAN_INTERVAL_HOURS),
        )
        self.entry = entry
        self.address_id: str = entry.data[CONF_ADDRESS_ID]
        self.lat: float = entry.data[CONF_LAT]
        self.lon: float = entry.data[CONF_LON]

    async def _async_update_data(self) -> dict:
        """Fetch data from Publidata API."""
        try:
            services = await self._fetch_services()
            return self._parse_services(services)
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Erreur API Publidata: {err}") from err

    async def _fetch_services(self) -> list[dict]:
        """Appelle l'endpoint search de l'API Publidata."""
        params = {
            "size": 999,
            "types[]": "Platform::Services::WasteCollection",
            "instances[]": API_INSTANCE_ID,
            "address_id": self.address_id,
            "lat": self.lat,
            "lon": self.lon,
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(API_SEARCH_URL, params=params) as resp:
                resp.raise_for_status()
                data = await resp.json()

        hits = data.get("hits", {}).get("hits", [])
        return [hit["_source"] for hit in hits]

    def _parse_services(self, services: list[dict]) -> dict:
        """
        Associe chaque type de collecte à ses prochaines dates
        en cherchant le service le plus précis (depth=1, sectorization=single)
        correspondant à l'adresse.
        """
        today = date.today()
        result = {}

        for collecte_key, collecte_info in COLLECTE_TYPES.items():
            garbage_types = collecte_info["garbage_types"]

            # Chercher le meilleur service pour ce type
            service = self._find_best_service(services, garbage_types)

            if service is None:
                _LOGGER.debug("Aucun service trouvé pour %s", collecte_key)
                result[collecte_key] = {
                    "prochaine_date": None,
                    "jours_restants": None,
                    "dates_futures": [],
                    "service_name": None,
                }
                continue

            opening_hours = service.get("opening_hours", "")

            if not opening_hours:
                _LOGGER.debug(
                    "Pas d'horaires pour %s (service: %s)",
                    collecte_key, service.get("name")
                )
                result[collecte_key] = {
                    "prochaine_date": None,
                    "jours_restants": None,
                    "dates_futures": [],
                    "service_name": service.get("name"),
                }
                continue

            next_date = prochaine_date(opening_hours, today)
            future_dates = dates_futures(opening_hours, today, max_dates=5)

            jours = (next_date - today).days if next_date else None

            result[collecte_key] = {
                "prochaine_date": next_date,
                "jours_restants": jours,
                "dates_futures": future_dates,
                "service_name": service.get("name"),
                "opening_hours_raw": opening_hours,
            }

            _LOGGER.debug(
                "%s → prochaine: %s (dans %s jours) — service: %s",
                collecte_key, next_date, jours, service.get("name")
            )

        return result

    def _find_best_service(
        self, services: list[dict], garbage_types: list[str]
    ) -> dict | None:
        """
        Trouve le service le plus pertinent pour un type de collecte.
        Priorité : depth=1 (secteur spécifique) > depth=0 (MRC général)
        Et seulement les services avec des schedules (opening_hours non vide).
        """
        candidates = []

        for service in services:
            metas = service.get("metas", {})
            svc_garbage_types = metas.get("garbage_types", [])

            # Vérifie si ce service correspond au type recherché
            if not any(gt in svc_garbage_types for gt in garbage_types):
                continue

            # Ignorer les services sans horaires (parents généraux)
            opening_hours = service.get("opening_hours", "")
            if not opening_hours:
                continue

            candidates.append(service)

        if not candidates:
            return None

        # Préférer depth=1 (service spécifique à la ville/secteur)
        specific = [s for s in candidates if s.get("depth", 0) >= 1]
        if specific:
            # Prendre celui avec le plus de schedules (le plus précis)
            return max(specific, key=lambda s: len(s.get("opening_hours", "")))

        # Sinon prendre le premier service général
        return candidates[0]
