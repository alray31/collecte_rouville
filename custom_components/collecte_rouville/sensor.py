"""Capteurs de date pour Collecte Rouville."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import CollecteCoordinator
from .const import COLLECTE_TYPES, CONF_VILLE, DOMAIN


def _jours_restants_texte(jours: int | None) -> str | None:
    """Convertit un nombre de jours en texte lisible."""
    if jours is None:
        return None
    if jours == 0:
        return "Aujourd'hui"
    if jours == 1:
        return "Demain"
    return f"Dans {jours} jours"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: CollecteCoordinator = hass.data[DOMAIN][entry.entry_id]
    ville = entry.data.get(CONF_VILLE, "")
    async_add_entities(
        CollecteSensor(coordinator, ctype, ville) for ctype in COLLECTE_TYPES
    )


class CollecteSensor(CoordinatorEntity, SensorEntity):
    """Capteur indiquant le délai avant la prochaine collecte."""

    def __init__(self, coordinator: CollecteCoordinator, ctype: str, ville: str) -> None:
        super().__init__(coordinator)
        self._ctype = ctype
        self._ville = ville
        meta = COLLECTE_TYPES[ctype]
        ville_slug = ville.lower().replace(" ", "_").replace("-", "_").replace("'", "_")

        self._attr_unique_id = f"{ville_slug}_collecte_{ctype}"
        self._attr_name = f"Collecte {meta['name']} – {ville}"
        self._attr_icon = meta["icon"]

    @property
    def _info(self) -> dict:
        if not self.coordinator.data:
            return {}
        return self.coordinator.data.get(self._ctype, {})

    @property
    def state(self) -> str | None:
        """Retourne le texte lisible : Aujourd'hui / Demain / Dans X jours."""
        return _jours_restants_texte(self._info.get("jours_restants"))

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        info = self._info
        prochaine = info.get("prochaine_date")
        return {
            "prochaine_date": prochaine.isoformat() if prochaine else None,
            "jours_restants": info.get("jours_restants"),
            "dates_futures": info.get("dates_futures", []),
            "summary_ics": info.get("summary"),
            "ville": self._ville,
        }

    @property
    def device_info(self):
        ville_slug = self._ville.lower().replace(" ", "_").replace("-", "_").replace("'", "_")
        return {
            "identifiers": {(DOMAIN, ville_slug)},
            "name": f"Collecte – {self._ville}",
            "manufacturer": "Publidata / MRC de Rouville",
            "model": "Calendrier ICS municipal",
        }
