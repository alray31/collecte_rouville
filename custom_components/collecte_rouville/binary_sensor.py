"""Binary sensors pour Collecte MRC de Rouville v3.0."""

from __future__ import annotations

from datetime import date, datetime, timedelta

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
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

    for collecte_key, collecte_info in COLLECTE_TYPES.items():
        # Binary sensor "sortir"
        entities.append(
            CollecteSortirBinarySensor(coordinator, entry, collecte_key, collecte_info)
        )
        # Binary sensor "inscription" pour volumineux et branches
        if collecte_key in COLLECTE_INSCRIPTION:
            entities.append(
                CollecteInscriptionBinarySensor(
                    coordinator, entry, collecte_key, collecte_info
                )
            )

    async_add_entities(entities)


class _CollecteBaseBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Classe de base avec réévaluation à la minute."""

    def __init__(
        self,
        coordinator: CollecteRouvilleCoordinator,
        entry: ConfigEntry,
        collecte_key: str,
        collecte_info: dict,
    ) -> None:
        super().__init__(coordinator)
        self._collecte_key = collecte_key
        self._collecte_info = collecte_info
        self._entry = entry
        self._unsub = None

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self._unsub = async_track_time_interval(
            self.hass,
            self._async_time_update,
            timedelta(minutes=1),
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
    """ON quand il faut sortir les bacs (12h avant jusqu'au lendemain soir)."""

    def __init__(self, coordinator, entry, collecte_key, collecte_info):
        super().__init__(coordinator, entry, collecte_key, collecte_info)
        ville = entry.data.get(CONF_VILLE, "")
        self._attr_unique_id = f"{entry.entry_id}_{collecte_key}_sortir"
        self._attr_name = f"Sortir {collecte_info['name']} - {ville}"
        self._attr_icon = collecte_info["icon"]

    @property
    def is_on(self) -> bool:
        prochaine = self._data.get("prochaine_date")
        if not prochaine:
            return False

        now = datetime.now()
        today = now.date()

        # Activation : minuit_J - 12h jusqu'à minuit_J + 24h
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
        if prochaine:
            activation = datetime.combine(prochaine, datetime.min.time()) - timedelta(
                hours=BINARY_SENSOR_HOURS_BEFORE
            )
        else:
            activation = None

        return {
            "prochaine_collecte": prochaine.isoformat() if prochaine else None,
            "jours_restants": data.get("jours_restants"),
            "activation_a_partir_de": activation.isoformat() if activation else None,
            "message": (
                f"Sortir les {self._collecte_info['name'].lower()} !"
                if self.is_on
                else None
            ),
            "adresse": self._entry.data.get(CONF_ADDRESS_LABEL),
        }


class CollecteInscriptionBinarySensor(_CollecteBaseBinarySensor):
    """ON pendant la fenêtre d'inscription (J-21 à J-8)."""

    def __init__(self, coordinator, entry, collecte_key, collecte_info):
        super().__init__(coordinator, entry, collecte_key, collecte_info)
        ville = entry.data.get(CONF_VILLE, "")
        self._attr_unique_id = f"{entry.entry_id}_{collecte_key}_inscription"
        self._attr_name = f"Inscription {collecte_info['name']} - {ville}"
        self._attr_icon = collecte_info["icon"]

    @property
    def is_on(self) -> bool:
        prochaine = self._data.get("prochaine_date")
        if not prochaine:
            return False

        today = date.today()
        jours = (prochaine - today).days
        return INSCRIPTION_JOURS_AVANT_FIN <= jours <= INSCRIPTION_JOURS_AVANT_DEBUT

    @property
    def extra_state_attributes(self) -> dict:
        data = self._data
        prochaine = data.get("prochaine_date")
        today = date.today()

        if prochaine:
            debut = prochaine - timedelta(days=INSCRIPTION_JOURS_AVANT_DEBUT)
            fin = prochaine - timedelta(days=INSCRIPTION_JOURS_AVANT_FIN)
        else:
            debut = fin = None

        return {
            "prochaine_collecte": prochaine.isoformat() if prochaine else None,
            "inscription_debut": debut.isoformat() if debut else None,
            "inscription_fin": fin.isoformat() if fin else None,
            "message": (
                f"Inscription {self._collecte_info['name'].lower()} ouverte !"
                if self.is_on
                else None
            ),
            "adresse": self._entry.data.get(CONF_ADDRESS_LABEL),
        }
