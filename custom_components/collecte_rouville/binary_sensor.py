"""Binary sensors pour Collecte Rouville — actifs 12h avant la collecte."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import CollecteCoordinator
from .const import BINARY_SENSOR_HOURS_BEFORE, COLLECTE_TYPES, CONF_VILLE, DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: CollecteCoordinator = hass.data[DOMAIN][entry.entry_id]
    ville = entry.data.get(CONF_VILLE, "")
    async_add_entities(
        CollecteBinarySensor(coordinator, ctype, ville) for ctype in COLLECTE_TYPES
    )


class CollecteBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """
    Binary sensor qui devient ON lorsqu'on est à moins de BINARY_SENSOR_HOURS_BEFORE
    heures du début de la prochaine collecte (minuit du jour J).

    La fenêtre d'activation est :
        [minuit_jour_J - HOURS_BEFORE, minuit_jour_J + 24h)
    soit le binary sensor reste ON toute la journée de collecte ET les X heures avant.
    """

    def __init__(self, coordinator: CollecteCoordinator, ctype: str, ville: str) -> None:
        super().__init__(coordinator)
        self._ctype = ctype
        self._ville = ville
        meta = COLLECTE_TYPES[ctype]
        ville_slug = ville.lower().replace(" ", "_").replace("-", "_").replace("'", "_")

        self._attr_unique_id = f"{ville_slug}_sortir_{ctype}"
        self._attr_name = f"Sortir {meta['name']} – {ville}"
        self._attr_icon = meta["icon"]
        self._message = meta["binary_message"]

    @property
    def _info(self) -> dict:
        if not self.coordinator.data:
            return {}
        return self.coordinator.data.get(self._ctype, {})

    @property
    def is_on(self) -> bool:
        """True si on est dans la fenêtre d'alerte (12h avant minuit du jour J)."""
        prochaine = self._info.get("prochaine_date")
        if prochaine is None:
            return False

        now = datetime.now()
        # Minuit du jour de collecte
        collecte_midnight = datetime(prochaine.year, prochaine.month, prochaine.day, 0, 0, 0)
        # Fenêtre : de (minuit - 12h) jusqu'à (minuit + 24h) = toute la journée de collecte
        window_start = collecte_midnight - timedelta(hours=BINARY_SENSOR_HOURS_BEFORE)
        window_end = collecte_midnight + timedelta(hours=24)

        return window_start <= now < window_end

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        info = self._info
        prochaine = info.get("prochaine_date")
        attrs: dict[str, Any] = {
            "message": self._message if self.is_on else None,
            "prochaine_collecte": prochaine.isoformat() if prochaine else None,
            "jours_restants": info.get("jours_restants"),
            "ville": self._ville,
            "heures_avant_activation": BINARY_SENSOR_HOURS_BEFORE,
        }
        if prochaine:
            collecte_midnight = datetime(prochaine.year, prochaine.month, prochaine.day)
            window_start = collecte_midnight - timedelta(hours=BINARY_SENSOR_HOURS_BEFORE)
            attrs["activation_a_partir_de"] = window_start.isoformat()
        return attrs

    @property
    def device_info(self):
        ville_slug = self._ville.lower().replace(" ", "_").replace("-", "_").replace("'", "_")
        return {
            "identifiers": {(DOMAIN, ville_slug)},
            "name": f"Collecte – {self._ville}",
            "manufacturer": "Publidata / MRC de Rouville",
            "model": "Calendrier ICS municipal",
        }
