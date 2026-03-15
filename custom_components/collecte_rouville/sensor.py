"""Sensors pour Collecte MRC de Rouville v3.0."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import CollecteRouvilleCoordinator
from .const import COLLECTE_TYPES, CONF_ADDRESS_LABEL, CONF_VILLE, DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors."""
    coordinator: CollecteRouvilleCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        CollecteSensor(coordinator, entry, key, info)
        for key, info in COLLECTE_TYPES.items()
    ]
    async_add_entities(entities)


class CollecteSensor(CoordinatorEntity, SensorEntity):
    """Sensor pour une collecte spécifique."""

    def __init__(self, coordinator, entry, collecte_key, collecte_info):
        super().__init__(coordinator)
        self._collecte_key = collecte_key
        self._collecte_info = collecte_info
        self._entry = entry

        ville = entry.data.get(CONF_VILLE, "")
        self._attr_unique_id = f"{entry.entry_id}_{collecte_key}_sensor"
        self._attr_name = collecte_info["name"]
        self._attr_icon = collecte_info["icon"]
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"Collecte {ville}",
            manufacturer="MRC de Rouville",
            model="Publidata API",
            entry_type="service",
        )

    @property
    def _data(self) -> dict:
        return self.coordinator.data.get(self._collecte_key, {})

    @property
    def native_value(self) -> str | None:
        """État = texte lisible."""
        jours = self._data.get("jours_restants")
        if jours is None:
            return "Aucune collecte prévue"
        if jours == 0:
            return "Aujourd'hui"
        if jours == 1:
            return "Demain"
        return f"Dans {jours} jours"

    @property
    def extra_state_attributes(self) -> dict:
        data = self._data
        prochaine = data.get("prochaine_date")
        futures = data.get("dates_futures", [])
        return {
            "prochaine_date": prochaine.isoformat() if prochaine else None,
            "jours_restants": data.get("jours_restants"),
            "dates_futures": [d.isoformat() for d in futures],
            "service_name": data.get("service_name"),
            "adresse": self._entry.data.get(CONF_ADDRESS_LABEL),
            "ville": self._entry.data.get(CONF_VILLE),
        }
