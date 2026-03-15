"""Binary sensors pour Collecte MRC de Rouville v3.0."""

from __future__ import annotations

from datetime import date, datetime, timedelta

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import CollecteRouvilleCoordinator
from .const import (
    BINARY_SENSOR_HOURS_BEFORE,
    COLLECTE_INSCRIPTION,
    COLLECTE_TYPES,
    CONF_ADDRESS_LABEL,
    CONF_VILLE,
    DOMAIN,
    INSCRIPTION_JOURS_AVANT_DEBUT,
    INSCRIPTION_JOURS_AVANT_FIN,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary sensors."""
    coordinator: CollecteRouvilleCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for key, info in COLLECTE_TYPES.items():
        entities.append(CollecteSortirBinarySensor(coordinator, entry, key, info))
        if key in COLLECTE_INSCRIPTION:
            entities.append(CollecteInscriptionBinarySensor(coordinator, entry, key, info))
    async_add_entities(entities)


def _device_info(entry: ConfigEntry) -> DeviceInfo:
    ville = entry.data.get(CONF_VILLE, "")
    return DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=f"Collecte {ville}",
        manufacturer="MRC de Rouville",
        model="Publidata API",
        entry_type="service",
    )


class _CollecteBaseBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Classe de base avec réévaluation à la minute."""

    def __init__(self, coordinator, entry, collecte_key, collecte_info):
        super().__init__(coordinator)
        self._collecte_key = collecte_key
        self._collecte_info = collecte_info
        self._entry = entry
        self._unsub = None
        self._attr_device_info = _device_info(entry)

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
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
        return self.coordinator.data.get(self._collecte_key, {})


class CollecteSortirBinarySensor(_CollecteBaseBinarySensor):
    """ON quand il faut sortir les bacs."""

    def __init__(self, coordinator, entry, collecte_key, collecte_info):
        super().__init__(coordinator, entry, collecte_key, collecte_info)
        self._attr_unique_id = f"{entry.entry_id}_{collecte_key}_sortir"
        self._attr_name = f"Sortir {collecte_info['name']}"
        self._attr_icon = collecte_info["icon"]

    @property
    def is_on(self) -> bool:
        prochaine = self._data.get("prochaine_date")
        if not prochaine:
            return False
        now = datetime.now()
        activation = datetime.combine(prochaine, datetime.min.time()) - timedelta(
            hours=BINARY_SENSOR_HOURS_BEFORE
        )
        desactivation = datetime.combine(
            prochaine + timedelta(days=1), datetime.min.time()
        ) + timedelta(hours=24)
        return activation <= now < desactivation

    @property
    def extra_state_attributes(self) -> dict:
        data = self._data
        prochaine = data.get("prochaine_date")
        activation = (
            datetime.combine(prochaine, datetime.min.time())
            - timedelta(hours=BINARY_SENSOR_HOURS_BEFORE)
        ) if prochaine else None
        return {
            "prochaine_collecte": prochaine.isoformat() if prochaine else None,
            "jours_restants": data.get("jours_restants"),
            "activation_a_partir_de": activation.isoformat() if activation else None,
            "message": f"Sortir les {self._collecte_info['name'].lower()} !" if self.is_on else None,
            "adresse": self._entry.data.get(CONF_ADDRESS_LABEL),
        }


class CollecteInscriptionBinarySensor(_CollecteBaseBinarySensor):
    """ON pendant la fenêtre d'inscription."""

    def __init__(self, coordinator, entry, collecte_key, collecte_info):
        super().__init__(coordinator, entry, collecte_key, collecte_info)
        self._attr_unique_id = f"{entry.entry_id}_{collecte_key}_inscription"
        self._attr_name = f"Inscription {collecte_info['name']}"
        self._attr_icon = collecte_info["icon"]

    @property
    def is_on(self) -> bool:
        prochaine = self._data.get("prochaine_date")
        if not prochaine:
            return False
        jours = (prochaine - date.today()).days
        return INSCRIPTION_JOURS_AVANT_FIN <= jours <= INSCRIPTION_JOURS_AVANT_DEBUT

    @property
    def extra_state_attributes(self) -> dict:
        data = self._data
        prochaine = data.get("prochaine_date")
        if prochaine:
            debut = prochaine - timedelta(days=INSCRIPTION_JOURS_AVANT_DEBUT)
            fin = prochaine - timedelta(days=INSCRIPTION_JOURS_AVANT_FIN)
        else:
            debut = fin = None
        return {
            "prochaine_collecte": prochaine.isoformat() if prochaine else None,
            "inscription_debut": debut.isoformat() if debut else None,
            "inscription_fin": fin.isoformat() if fin else None,
            "message": f"Inscription {self._collecte_info['name'].lower()} ouverte !" if self.is_on else None,
            "adresse": self._entry.data.get(CONF_ADDRESS_LABEL),
        }
