"""Constants for Collecte MRC de Rouville - v1.0 (API REST)."""

DOMAIN = "collecte_rouville"

# API Publidata
API_BASE_URL = "https://api.publidata.ca/v2"
API_INSTANCE_ID = 21
API_GEOCODER_URL = f"{API_BASE_URL}/geocoder"
API_SEARCH_URL = f"{API_BASE_URL}/search"

# Polling
SCAN_INTERVAL_HOURS = 1

# Binary sensor
BINARY_SENSOR_HOURS_BEFORE = 12  # activer 12h avant la collecte

# Binary sensor inscription (volumineux + branches)
INSCRIPTION_JOURS_AVANT_DEBUT = 21
INSCRIPTION_JOURS_AVANT_FIN = 8
COLLECTE_INSCRIPTION = ["volumineux", "branches"]

# Villes supportées → insee_code (citycode)
VILLES = {
    "Ange-Gardien": "55008",
    "Marieville": "55048",
    "Richelieu": "55057",
    "Rougemont": "55037",
    "Saint-Césaire": "55023",
    "Saint-Mathias-sur-Richelieu": "55065",
    "Saint-Paul-d'Abbotsford": "55015",
    "Sainte-Angèle-de-Monnoir": "55030",
}

# Types de collecte : clé interne → garbage_type Publidata + icône
COLLECTE_TYPES = {
    "volumineux": {
        "garbage_types": ["enc"],
        "icon": "mdi:sofa",
        "name": "Volumineux",
    },
    "recuperation": {
        "garbage_types": ["jrm"],
        "icon": "mdi:recycle",
        "name": "Récupération",
    },
    "ordures": {
        "garbage_types": ["omr"],
        "icon": "mdi:trash-can",
        "name": "Ordures ménagères",
    },
    "pellicules_agricoles": {
        "garbage_types": ["bio"],
        "icon": "mdi:barley",
        "name": "Pellicules agricoles",
    },
    "residus_verts": {
        "garbage_types": ["dv"],
        "icon": "mdi:grass",
        "name": "Résidus verts",
    },
    "compost_alimentaire": {
        "garbage_types": ["alim"],
        "icon": "mdi:compost",
        "name": "Résidus alimentaires",
    },
    "branches": {
        "garbage_types": ["bois"],
        "icon": "mdi:tree",
        "name": "Branches",
    },
}

# Config flow keys
CONF_VILLE = "ville"
CONF_ADRESSE = "adresse"
CONF_ADDRESS_ID = "address_id"
CONF_LAT = "lat"
CONF_LON = "lon"
CONF_ADDRESS_LABEL = "address_label"

# Écocentres — IDs fixes pour toute la MRC
ECOCENTRES = {
    "marieville": {
        "name": "Écocentre de Marieville",
        "facility_id": 31,
        "service_id": 1269,
        "icon": "mdi:recycle",
        "adresse": "135 ch. du Ruisseau Saint-Louis Est, Marieville",
    },
    "saint_cesaire": {
        "name": "Écocentre de Saint-Césaire",
        "facility_id": 34,
        "service_id": 1338,
        "icon": "mdi:recycle",
        "adresse": "275 route 112, Saint-Césaire",
    },
}

API_FACILITY_URL = f"{API_BASE_URL}/search"
