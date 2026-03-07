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
# Les mots-clés correspondent aux noms EXACTS utilisés dans les SUMMARY Publidata
# Format ICS : "Collecte en porte à porte (Nom du type)"
# La recherche se fait en lowercase sur le texte complet du SUMMARY + DESCRIPTION.
#
# NOTE: Publidata regroupe Journaux + Revues dans un seul événement :
#   "Collecte en porte à porte (Journaux, Revues et Magazines)"
#   → un seul capteur "journaux_revues" couvre les deux.

COLLECTE_TYPES: dict[str, dict] = {
    "encombrants": {
        "name": "Encombrants",
        "icon": "mdi:dump-truck",
        "binary_message": "Sortir les encombrants maintenant",
        # Correspond à : (Encombrants)
        "keywords": ["encombrants", "encombrant"],
    },
    "journaux_revues": {
        "name": "Journaux, Revues et Magazines",
        "icon": "mdi:newspaper",
        "binary_message": "Sortir les journaux et magazines maintenant",
        # Correspond à : (Journaux, Revues et Magazines)
        "keywords": ["journaux", "revues et magazines", "journaux, revues"],
    },
    "ordures": {
        "name": "Ordures Ménagères Résiduelles",
        "icon": "mdi:trash-can",
        "binary_message": "Sortir les ordures ménagères maintenant",
        # Correspond à : (Ordures Ménagères Résiduelles)
        "keywords": ["ordures ménagères résiduelles", "ordures ménagères", "ordures"],
    },
    "biochets_organiques": {
        "name": "Biodéchets et Déchets Organiques",
        "icon": "mdi:leaf",
        "binary_message": "Sortir les biodéchets et déchets organiques maintenant",
        # Correspond à : (Biodéchets et Déchets organiques)
        "keywords": ["biodéchets et déchets organiques", "biodéchets", "déchets organiques"],
    },
    "dechets_vegetaux": {
        "name": "Déchets Végétaux",
        "icon": "mdi:tree",
        "binary_message": "Sortir les déchets végétaux maintenant",
        # Correspond à : (Déchets Végétaux)
        "keywords": ["déchets végétaux", "déchets végétal"],
    },
    "dechets_alimentaires": {
        "name": "Déchets Alimentaires",
        "icon": "mdi:food-apple",
        "binary_message": "Sortir les déchets alimentaires maintenant",
        # Correspond à : (Déchets alimentaires)
        "keywords": ["déchets alimentaires"],
    },
    "bois": {
        "name": "Bois",
        "icon": "mdi:forest",
        "binary_message": "Sortir le bois maintenant",
        # Correspond à : (Bois)
        "keywords": ["(bois)"],
    },
}
