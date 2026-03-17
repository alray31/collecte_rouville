"""Sensors et binary sensors pour les écocentres MRC de Rouville v1.0."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import CollecteRouvilleCoordinator
from .const import CONF_VILLE, DOMAIN, ECOCENTRES


def _device_info(entry: ConfigEntry) -> DeviceInfo:
    ville = entry.data.get(CONF_VILLE, "")
    return DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=f"Collecte {ville}",
        manufacturer="MRC de Rouville",
        model="Publidata API",
        entry_type="service",
    )


def create_ecocentre_entities(coordinator, entry):
    """Crée les entités pour les deux écocentres."""
    entities = []
    for key, info in ECOCENTRES.items():
        entities.append(EcocentreOuvertBinarySensor(coordinator, entry, key, info))
        entities.append(EcocentreProchaineSensor(coordinator, entry, key, info))
    return entities


class EcocentreOuvertBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor : écocentre ouvert/fermé en ce moment."""

    _attr_device_class = BinarySensorDeviceClass.OPENING

    def __init__(self, coordinator, entry, eco_key, eco_info):
        super().__init__(coordinator)
        self._eco_key = eco_key
        self._eco_info = eco_info
        self._entry = entry
        self._unsub = None
        self._attr_unique_id = f"{entry.entry_id}_{eco_key}_ouvert"
        self._attr_name = f"{eco_info['name']}"
        self._attr_icon = eco_info["icon"]
        self._attr_device_info = _device_info(entry)

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        # Réévaluer toutes les minutes (l'état change à l'heure d'ouverture/fermeture)
        self._unsub = async_track_time_interval(
            self.hass, self._async_time_update, timedelta(minutes=1)
        )

    async def async_will_remove_from_hass(self) -> None:
        if self._unsub:
            self._unsub()

    async def _async_time_update(self, _now=None) -> None:
        self.async_write_ha_state()

    @property
    def _data(self) -> dict:
        return self.coordinator.data.get(f"ecocentre_{self._eco_key}", {})

    @property
    def is_on(self) -> bool:
        return self._data.get("is_open", False)

    @property
    def extra_state_attributes(self) -> dict:
        data = self._data
        prochaine = data.get("prochaine_ouverture")
        return {
            "adresse": self._eco_info["adresse"],
            "prochaine_ouverture": prochaine.isoformat() if prochaine else None,
        }


class EcocentreProchaineSensor(CoordinatorEntity, SensorEntity):
    """Sensor : date/heure de la prochaine ouverture de l'écocentre."""

    def __init__(self, coordinator, entry, eco_key, eco_info):
        super().__init__(coordinator)
        self._eco_key = eco_key
        self._eco_info = eco_info
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_{eco_key}_prochaine_ouverture"
        self._attr_name = f"{eco_info['name']} - Prochaine ouverture"
        self._attr_icon = eco_info["icon"]
        self._attr_device_info = _device_info(entry)

    @property
    def _data(self) -> dict:
        return self.coordinator.data.get(f"ecocentre_{self._eco_key}", {})

    @property
    def native_value(self) -> str | None:
        """Retourne la prochaine ouverture en texte lisible."""
        prochaine = self._data.get("prochaine_ouverture")
        if not prochaine:
            return "Aucune ouverture prévue"
        from datetime import date
        today = date.today()
        delta = (prochaine.date() - today).days
        heure = prochaine.strftime("%H:%M")
        if delta == 0:
            return f"Aujourd'hui à {heure}"
        if delta == 1:
            return f"Demain à {heure}"
        # Formatter la date en français
        MOIS = ["jan","fév","mar","avr","mai","jun","jul","aoû","sep","oct","nov","déc"]
        mois = MOIS[prochaine.month - 1]
        return f"{prochaine.day} {mois} à {heure}"

    @property
    def extra_state_attributes(self) -> dict:
        data = self._data
        prochaine = data.get("prochaine_ouverture")
        return {
            "is_open": data.get("is_open", False),
            "adresse": self._eco_info["adresse"],
            "prochaine_ouverture": prochaine.isoformat() if prochaine else None,
        }
