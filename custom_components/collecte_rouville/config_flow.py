"""Config flow pour Collecte MRC de Rouville v3.0."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    API_GEOCODER_URL,
    CONF_ADDRESS_ID,
    CONF_ADDRESS_LABEL,
    CONF_ADRESSE,
    CONF_LAT,
    CONF_LON,
    CONF_VILLE,
    DOMAIN,
    VILLES,
)

_LOGGER = logging.getLogger(__name__)


class CollecteRouvilleConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow en 2 étapes : ville → adresse."""

    VERSION = 3

    def __init__(self) -> None:
        self._ville: str = ""
        self._citycode: str = ""
        self._adresse_query: str = ""
        self._suggestions: dict[str, dict] = {}  # label → {address_id, lat, lon}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Étape 1 : Choisir la ville."""
        errors = {}

        if user_input is not None:
            self._ville = user_input[CONF_VILLE]
            self._citycode = VILLES[self._ville]
            return await self.async_step_adresse()

        schema = vol.Schema({
            vol.Required(CONF_VILLE): vol.In(sorted(VILLES.keys()))
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_adresse(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Étape 2 : Taper l'adresse pour géocodage."""
        errors = {}

        if user_input is not None:
            self._adresse_query = user_input[CONF_ADRESSE]
            # Appeler le géocodeur
            suggestions = await self._geocode(self._adresse_query)
            if not suggestions:
                errors[CONF_ADRESSE] = "adresse_non_trouvee"
            else:
                self._suggestions = suggestions
                return await self.async_step_choisir_adresse()

        schema = vol.Schema({
            vol.Required(CONF_ADRESSE): str,
        })

        return self.async_show_form(
            step_id="adresse",
            data_schema=schema,
            errors=errors,
            description_placeholders={
                "ville": self._ville,
                "widget_url": "https://widget.publidata.ca/NKx0JtQVX3/",
            },
        )

    async def async_step_choisir_adresse(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Étape 3 : Choisir parmi les suggestions."""
        errors = {}

        if user_input is not None:
            label = user_input["adresse_choisie"]
            info = self._suggestions[label]

            # Vérifier unicité
            await self.async_set_unique_id(info["address_id"])
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=label,
                data={
                    CONF_VILLE: self._ville,
                    CONF_ADDRESS_ID: info["address_id"],
                    CONF_LAT: info["lat"],
                    CONF_LON: info["lon"],
                    CONF_ADDRESS_LABEL: label,
                },
            )

        schema = vol.Schema({
            vol.Required("adresse_choisie"): vol.In(list(self._suggestions.keys()))
        })

        return self.async_show_form(
            step_id="choisir_adresse",
            data_schema=schema,
            errors=errors,
        )

    async def _geocode(self, query: str) -> dict[str, dict]:
        """Appelle l'API géocodeur Publidata."""
        params = {
            "q": query,
            "limit": 10,
            "lookup": "publidata",
            "citycode": self._citycode,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(API_GEOCODER_URL, params=params) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
        except aiohttp.ClientError as err:
            _LOGGER.error("Erreur géocodage: %s", err)
            return {}

        suggestions = {}
        # La réponse est une liste avec un objet data contenant features
        items = data if isinstance(data, list) else [data]
        for item in items:
            features = item.get("data", {}).get("features", [])
            for feature in features:
                props = feature.get("properties", {})
                coords = feature.get("geometry", {}).get("coordinates", [])

                # Seulement les adresses avec numéro civique
                if props.get("type") != "housenumber":
                    continue

                label_raw = props.get("label", "")
                address_id = props.get("id", "")
                if not label_raw or not address_id or len(coords) < 2:
                    continue

                # Enlever le code postal du label (ex: "J3L 6Z5 ")
                import re
                label = re.sub(r"\b[A-Z]\d[A-Z]\s?\d[A-Z]\d\b\s*", "", label_raw).strip()

                suggestions[label] = {
                    "address_id": address_id,
                    "lon": coords[0],
                    "lat": coords[1],
                }

        return suggestions
