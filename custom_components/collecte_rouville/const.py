"""Constantes pour l'intégration Collecte Rouville."""

DOMAIN = "collecte_rouville"
CONF_ICS_URL = "ics_url"
CONF_VILLE = "ville"
SCAN_INTERVAL_HOURS = 12

# Heures avant l'événement pour activer le binary sensor
BINARY_SENSOR_HOURS_BEFORE = 12

# ─── Villes disponibles et leurs URLs ICS ────────────────────────────────────
VILLES: dict[str, dict] = {
    "St-Césaire": {
        "ics_url": "https://export.publidata.ca/ics/87obbcRMVQ,OxM11cqZxm,gLbyycz6xJ,o7EYYc9875,8Vvllce5xv,B72PPcOrLO,B72PPcl6LO",
    },
    "St-Mathias-sur-Richelieu": {
        "ics_url": "https://export.publidata.ca/ics/g7WWWcog7q,MxQppcwR7l,2VXddc4DVN,E79ddc53VM,jVJZZc2PVR,gLbyycgQxJ,YVYwwcrzxD",
    },
    "Ange-Gardien": {
        "ics_url": "https://export.publidata.ca/ics/jVJZZc3aVR,RL3JJcydxN,2VXddcY1VN,2VXddcXDVN,NL5NNcZzVW,OxM11c6Axm,DVAbbcpa7X",
    },
    "Marieville": {
        "ics_url": "https://export.publidata.ca/ics/0Ly44cPBxB,D74ppcrP78,DLkKKcrnLa,jVJZZcmPVR,y7KbbcEeVv,YVYwwc4ExD,axGoocvpxN",
    },
    "Richelieu": {
        "ics_url": "https://export.publidata.ca/ics/y7Kbbc3KVv,QV8GGc3BLO,DLkKKcr5La,DLkKKcvnLa,Kx0KKcE87X,MxQppcvm7l,G7jGGcDdxg",
    },
    "Rougemont": {
        "ics_url": "https://export.publidata.ca/ics/o7EYYcmz75,KVq11cE3Vw,y7KbbcMKVv,y7KbbcyeVv,NLwaacbE7D,Q7Booc1rxb,d7D99cwoxB",
    },
    "Saint-Paul-d'Abbotsford": {
        "ics_url": "https://export.publidata.ca/ics/axGooc3qxN,Kx0KKcGg7X,J7dwwcBdVB,eVgGGcgdVo,G7jGGcXQxg,jVJZZcn2VR,E79ddclJVM",
    },
    "Sainte-Angèle-de-Monnoir": {
        "ics_url": "https://export.publidata.ca/ics/E79ddc3nVM,EVeXXcYOLB,YVYwwceAxD,87obbcebVQ,2VXddcODVN,DVAbbcYm7X,gLbyycEkxJ",
    },
}

VILLES_LIST = list(VILLES.keys())

# ─── Types de collecte ────────────────────────────────────────────────────────
# Clé interne → { name, keywords, icon, binary_sensor_message }
COLLECTE_TYPES: dict[str, dict] = {
    "encombrants": {
        "name": "Encombrants",
        "icon": "mdi:dump-truck",
        "binary_message": "Sortir les encombrants maintenant",
        "keywords": [
            "encombrant", "résidus domestiques dangereux", "rdd",
            "volumineux", "hors normes", "collecte spéciale",
        ],
    },
    "journaux": {
        "name": "Journaux",
        "icon": "mdi:newspaper",
        "binary_message": "Sortir les journaux maintenant",
        "keywords": [
            "journal", "journaux",
        ],
    },
    "revues": {
        "name": "Revues et Magazines",
        "icon": "mdi:book-open-page-variant",
        "binary_message": "Sortir les revues et magazines maintenant",
        "keywords": [
            "revue", "magazine", "périodique",
        ],
    },
    "ordures": {
        "name": "Ordures Ménagères Résiduelles",
        "icon": "mdi:trash-can",
        "binary_message": "Sortir les ordures ménagères maintenant",
        "keywords": [
            "ordure", "ménagère", "résiduelle", "bac noir", "poubelle",
            "déchets résiduels", "ordures ménagères",
        ],
    },
    "biochets_organiques": {
        "name": "Biodéchets et Déchets Organiques",
        "icon": "mdi:leaf",
        "binary_message": "Sortir les biodéchets et déchets organiques maintenant",
        "keywords": [
            "biodéchet", "organique", "bac brun", "matières organiques",
            "compost", "résidus organiques",
        ],
    },
    "dechets_vegetaux": {
        "name": "Déchets Végétaux",
        "icon": "mdi:tree",
        "binary_message": "Sortir les déchets végétaux maintenant",
        "keywords": [
            "végétal", "végétaux", "feuilles mortes", "gazon", "taille",
            "élagage", "branche", "herbe",
        ],
    },
    "dechets_alimentaires": {
        "name": "Déchets Alimentaires",
        "icon": "mdi:food-apple",
        "binary_message": "Sortir les déchets alimentaires maintenant",
        "keywords": [
            "alimentaire", "aliment", "nourriture", "résidus alimentaires",
            "table", "cuisine",
        ],
    },
    "bois": {
        "name": "Bois",
        "icon": "mdi:forest",
        "binary_message": "Sortir le bois maintenant",
        "keywords": [
            "bois", "bûche", "bûches", "palette", "planche",
        ],
    },
}
