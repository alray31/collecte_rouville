# collecte_rouville
🗑️ Intégration HACS Home Assistant pour les collectes municipales de la MRC de Rouville (Publidata ICS) — capteurs de dates et alertes automatiques.


## Villes supportées
- St-Césaire
- St-Mathias-sur-Richelieu
- Ange-Gardien
- Marieville
- Richelieu
- Rougemont
- Saint-Paul-d'Abbotsford
- Sainte-Angèle-de-Monnoir

---

## Entités créées (par ville)

### Capteurs (`sensor.*`)
| Entité | Description |
|--------|-------------|
| `sensor.collecte_encombrants_stcesaire` | Prochaine date — Encombrants |
| `sensor.collecte_journaux_stcesaire` | Prochaine date — Journaux |
| `sensor.collecte_revues_stcesaire` | Prochaine date — Revues et Magazines |
| `sensor.collecte_ordures_stcesaire` | Prochaine date — Ordures Ménagères Résiduelles |
| `sensor.collecte_biochets_organiques_stcesaire` | Prochaine date — Biodéchets et Déchets Organiques |
| `sensor.collecte_dechets_vegetaux_stcesaire` | Prochaine date — Déchets Végétaux |
| `sensor.collecte_dechets_alimentaires_stcesaire` | Prochaine date — Déchets Alimentaires |
| `sensor.collecte_bois_stcesaire` | Prochaine date — Bois |

**État** : Date ISO (ex: `2025-04-08`)  
**Attributs** : `jours_restants`, `dates_futures`, `summary_ics`, `ville`

### Binary Sensors (`binary_sensor.*`)
Chaque type de collecte dispose d'un binary sensor qui devient **ON** 12 heures avant minuit du jour de collecte et reste actif toute la journée.

| Entité | Se déclenche |
|--------|-------------|
| `binary_sensor.sortir_encombrants_stcesaire` | 12h avant les Encombrants |
| `binary_sensor.sortir_journaux_stcesaire` | 12h avant les Journaux |
| `binary_sensor.sortir_revues_stcesaire` | 12h avant les Revues |
| `binary_sensor.sortir_ordures_stcesaire` | 12h avant les Ordures |
| `binary_sensor.sortir_biochets_organiques_stcesaire` | 12h avant les Biodéchets |
| `binary_sensor.sortir_dechets_vegetaux_stcesaire` | 12h avant les Déchets végétaux |
| `binary_sensor.sortir_dechets_alimentaires_stcesaire` | 12h avant les Déchets alimentaires |
| `binary_sensor.sortir_bois_stcesaire` | 12h avant le Bois |

**Attributs** : `message`, `prochaine_collecte`, `jours_restants`, `activation_a_partir_de`

---

## Installation

### Manuel
1. Copier `custom_components/collecte_rouville/` dans `config/custom_components/`
2. Redémarrer Home Assistant
3. **Paramètres → Appareils et services → Ajouter une intégration**
4. Rechercher **Collecte MRC de Rouville**
5. Choisir votre ville dans la liste déroulante

### Via HACS
1. HACS → Intégrations → ⋮ → Dépôts personnalisés
2. Ajouter l'URL du dépôt GitHub, catégorie **Integration**
3. Installer et redémarrer HA

---

## Exemples d'automatisations

### Notification quand il faut sortir les bacs
```yaml
automation:
  - alias: "Rappel sortir les bacs"
    trigger:
      - platform: state
        entity_id:
          - binary_sensor.sortir_ordures_stcesaire
          - binary_sensor.sortir_biochets_organiques_stcesaire
          - binary_sensor.sortir_dechets_vegetaux_stcesaire
        to: "on"
    action:
      - service: notify.mobile_app_mon_telephone
        data:
          title: "🗑️ Collecte demain !"
          message: "{{ trigger.to_state.attributes.message }}"
```

### Carte Lovelace avec binary sensors
```yaml
type: entities
title: 🗑️ Collectes – St-Césaire
entities:
  - entity: binary_sensor.sortir_ordures_stcesaire
    name: "Sortir les ordures ?"
  - entity: sensor.collecte_ordures_stcesaire
    name: "Prochaine date ordures"
  - entity: binary_sensor.sortir_biochets_organiques_stcesaire
    name: "Sortir le compost ?"
  - entity: sensor.collecte_biochets_organiques_stcesaire
    name: "Prochaine date compost"
  - entity: binary_sensor.sortir_dechets_vegetaux_stcesaire
    name: "Sortir les déchets végétaux ?"
  - entity: sensor.collecte_dechets_vegetaux_stcesaire
    name: "Prochaine date déchets végétaux"
```

