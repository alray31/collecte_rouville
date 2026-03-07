"""Constantes pour l'intégration Collecte Rouville."""

DOMAIN = "collecte_rouville"
CONF_ICS_URL = "ics_url"
CONF_VILLE = "ville"
SCAN_INTERVAL_HOURS = 12

# Heures avant l'événement pour activer le binary sensor "sortir les bacs"
BINARY_SENSOR_HOURS_BEFORE = 12

# Fenêtre d'inscription pour les collectes sur inscription (en jours)
# Actif de INSCRIPTION_JOURS_AVANT_DEBUT à INSCRIPTION_JOURS_AVANT_FIN jours avant la collecte
INSCRIPTION_JOURS_AVANT_DEBUT = 21  # s'active 21 jours avant
INSCRIPTION_JOURS_AVANT_FIN = 8     # se désactive 8 jours avant

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
#
# binary_sensor_type :
#   "sortir"       → actif 12h avant minuit du jour J (toute la journée)
#   "inscription"  → actif de J-21 à J-8 (fenêtre pour s'inscrire)

COLLECTE_TYPES: dict[str, dict] = {
    "volumineux": {
        "name": "Collecte volumineux sur inscription",
        "icon": "mdi:sofa",
        "binary_message": "Sortir les volumineux maintenant",
        "binary_sensor_type": "sortir",
        # Correspond à : (Encombrants)
        "keywords": ["encombrants", "encombrant"],
    },
    "recuperation": {
        "name": "Récupération",
        "icon": "mdi:recycle",
        "binary_message": "Sortir la récupération maintenant",
        "binary_sensor_type": "sortir",
        # Correspond à : (Journaux, Revues et Magazines)
        "keywords": ["journaux", "revues et magazines", "journaux, revues"],
    },
    "ordures": {
        "name": "Ordures Ménagères Résiduelles",
        "icon": "mdi:trash-can",
        "binary_message": "Sortir les ordures ménagères maintenant",
        "binary_sensor_type": "sortir",
        # Correspond à : (Ordures Ménagères Résiduelles)
        "keywords": ["ordures ménagères résiduelles", "ordures ménagères", "ordures"],
    },
    "pellicules_agricoles": {
        "name": "Collecte de pellicules agricoles",
        "icon": "mdi:barley",
        "binary_message": "Sortir les pellicules agricoles maintenant",
        "binary_sensor_type": "sortir",
        # Correspond à : (Biodéchets et Déchets organiques)
        "keywords": ["biodéchets et déchets organiques", "biodéchets", "déchets organiques"],
    },
    "residus_verts": {
        "name": "Collecte résidus verts",
        "icon": "mdi:grass",
        "binary_message": "Sortir les résidus verts maintenant",
        "binary_sensor_type": "sortir",
        # Correspond à : (Déchets Végétaux)
        "keywords": ["déchets végétaux", "déchets végétal"],
    },
    "compost_alimentaire": {
        "name": "Collecte compost / déchets alimentaires",
        "icon": "mdi:compost",
        "binary_message": "Sortir le compost et déchets alimentaires maintenant",
        "binary_sensor_type": "sortir",
        # Correspond à : (Déchets alimentaires)
        "keywords": ["déchets alimentaires"],
    },
    "branches": {
        "name": "Collecte de branches sur inscription",
        "icon": "mdi:tree",
        "binary_message": "Sortir les branches maintenant",
        "binary_sensor_type": "sortir",
        # Correspond à : (Bois)
        "keywords": ["(bois)"],
    },
}

# Types de collecte qui ont un binary sensor d'inscription (J-21 à J-8)
# en PLUS du binary sensor "sortir" standard
COLLECTE_INSCRIPTION: list[str] = ["volumineux", "branches"]
