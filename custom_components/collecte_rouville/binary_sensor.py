"""Binary sensors pour Collecte Rouville."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import CollecteCoordinator
from .const import (
    BINARY_SENSOR_HOURS_BEFORE,
    COLLECTE_INSCRIPTION,
    COLLECTE_TYPES,
    CONF_VILLE,
    DOMAIN,
    INSCRIPTION_JOURS_AVANT_DEBUT,
    INSCRIPTION_JOURS_AVANT_FIN,
)

# Réévaluation de l'état ON/OFF toutes les minutes
# (indépendamment du polling ICS)
REEVALUATION_INTERVAL = timedelta(minutes=1)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: CollecteCoordinator = hass.data[DOMAIN][entry.entry_id]
    ville = entry.data.get(CONF_VILLE, "")

    entities = []
    for ctype in COLLECTE_TYPES:
        entities.append(CollecteSortirBinarySensor(coordinator, ctype, ville))
        if ctype in COLLECTE_INSCRIPTION:
            entities.append(CollecteInscriptionBinarySensor(coordinator, ctype, ville))

    async_add_entities(entities)


def _ville_slug(ville: str) -> str:
    return ville.lower().replace(" ", "_").replace("-", "_").replace("'", "_")


class _CollecteBaseBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """
    Classe de base pour les binary sensors de collecte.
    Ajoute une réévaluation toutes les minutes via async_track_time_interval
    pour que le passage ON/OFF soit précis à la minute, indépendamment
    de la fréquence de polling du coordinator.
    """

    def __init__(self, coordinator: CollecteCoordinator, ctype: str, ville: str) -> None:
        super().__init__(coordinator)
        self._ctype = ctype
        self._ville = ville
        self._unsub_timer = None

    async def async_added_to_hass(self) -> None:
        """Démarrer le timer de réévaluation à la minute."""
        await super().async_added_to_hass()

        @callback
        def _reevaluate(_now: datetime) -> None:
            """Forcer HA à relire is_on sans refetcher le ICS."""
            self.async_write_ha_state()

        self._unsub_timer = async_track_time_interval(
            self.hass, _reevaluate, REEVALUATION_INTERVAL
        )

    async def async_will_remove_from_hass(self) -> None:
        """Annuler le timer à la suppression de l'entité."""
        if self._unsub_timer:
            self._unsub_timer()
            self._unsub_timer = None

    @property
    def _info(self) -> dict:
        if not self.coordinator.data:
            return {}
        return self.coordinator.data.get(self._ctype, {})

    @property
    def device_info(self):
        slug = _ville_slug(self._ville)
        return {
            "identifiers": {(DOMAIN, slug)},
            "name": f"Collecte – {self._ville}",
            "manufacturer": "Publidata / MRC de Rouville",
            "model": "Calendrier ICS municipal",
        }


class CollecteSortirBinarySensor(_CollecteBaseBinarySensor):
    """
    Actif 12h avant minuit du jour de collecte, reste ON toute la journée.
    Fenêtre : [minuit_J - 12h,  minuit_J + 24h)
    Réévalué à la minute près grâce au timer hérité.
    """

    def __init__(self, coordinator: CollecteCoordinator, ctype: str, ville: str) -> None:
        super().__init__(coordinator, ctype, ville)
        meta = COLLECTE_TYPES[ctype]
        slug = _ville_slug(ville)

        self._attr_unique_id = f"{slug}_sortir_{ctype}"
        self._attr_name = f"Sortir – {meta['name']} – {ville}"
        self._attr_icon = meta["icon"]
        self._message = meta["binary_message"]

    @property
    def is_on(self) -> bool:
        prochaine = self._info.get("prochaine_date")
        if prochaine is None:
            return False
        now = datetime.now()
        midnight = datetime(prochaine.year, prochaine.month, prochaine.day)
        return (midnight - timedelta(hours=BINARY_SENSOR_HOURS_BEFORE)) <= now < (midnight + timedelta(hours=24))

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
            midnight = datetime(prochaine.year, prochaine.month, prochaine.day)
            attrs["activation_a_partir_de"] = (midnight - timedelta(hours=BINARY_SENSOR_HOURS_BEFORE)).isoformat()
        return attrs


class CollecteInscriptionBinarySensor(_CollecteBaseBinarySensor):
    """
    Actif de J-21 à J-8 avant la collecte sur inscription.
    Fenêtre : [minuit_J - 21 jours,  minuit_J - 8 jours)
    Réévalué à la minute près grâce au timer hérité.
    """

    def __init__(self, coordinator: CollecteCoordinator, ctype: str, ville: str) -> None:
        super().__init__(coordinator, ctype, ville)
        meta = COLLECTE_TYPES[ctype]
        slug = _ville_slug(ville)

        self._attr_unique_id = f"{slug}_inscription_{ctype}"

        if ctype == "volumineux":
            self._attr_name = f"S'inscrire – Collecte volumineux – {ville}"
            self._message = "S'inscrire à la collecte des volumineux maintenant"
        elif ctype == "branches":
            self._attr_name = f"S'inscrire – Collecte de branches – {ville}"
            self._message = "S'inscrire à la collecte de branches maintenant"
        else:
            self._attr_name = f"S'inscrire – {meta['name']} – {ville}"
            self._message = f"S'inscrire à la collecte – {meta['name']}"

        self._attr_icon = meta["icon"]

    @property
    def is_on(self) -> bool:
        prochaine = self._info.get("prochaine_date")
        if prochaine is None:
            return False
        now = datetime.now()
        midnight = datetime(prochaine.year, prochaine.month, prochaine.day)
        window_start = midnight - timedelta(days=INSCRIPTION_JOURS_AVANT_DEBUT)
        window_end   = midnight - timedelta(days=INSCRIPTION_JOURS_AVANT_FIN)
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
            "fenetre_inscription": f"J-{INSCRIPTION_JOURS_AVANT_DEBUT} à J-{INSCRIPTION_JOURS_AVANT_FIN}",
        }
        if prochaine:
            midnight = datetime(prochaine.year, prochaine.month, prochaine.day)
            attrs["inscription_debut"] = (midnight - timedelta(days=INSCRIPTION_JOURS_AVANT_DEBUT)).isoformat()
            attrs["inscription_fin"]   = (midnight - timedelta(days=INSCRIPTION_JOURS_AVANT_FIN)).isoformat()
        return attrs
