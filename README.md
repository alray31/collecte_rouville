# 🗑️ Collecte MRC de Rouville — Intégration HACS Home Assistant

🗑️ Intégration HACS Home Assistant pour les collectes municipales de la MRC de Rouville — capteurs de dates et alertes automatiques.

[![Ouvrir dans HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=alray31&repository=collecte_rouville&category=integration)

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
| `sensor.collecte_volumineux_sur_inscription_stcesaire` | Prochaine date — Collecte volumineux sur inscription |
| `sensor.recuperation_stcesaire` | Prochaine date — Récupération |
| `sensor.ordures_menageres_residuelles_stcesaire` | Prochaine date — Ordures Ménagères Résiduelles |
| `sensor.collecte_de_pellicules_agricoles_stcesaire` | Prochaine date — Collecte de pellicules agricoles |
| `sensor.collecte_residus_verts_stcesaire` | Prochaine date — Collecte résidus verts |
| `sensor.collecte_compost_dechets_alimentaires_stcesaire` | Prochaine date — Collecte compost / déchets alimentaires |
| `sensor.collecte_de_branches_sur_inscription_stcesaire` | Prochaine date — Collecte de branches sur inscription |

**État** : Date ISO (ex: `2026-04-08`)  
**Attributs** : `jours_restants`, `dates_futures`, `summary_ics`, `ville`

---

### Binary Sensors (`binary_sensor.*`)

#### Alertes "Sortir les bacs" — actifs 12h avant minuit du jour de collecte, restent ON toute la journée

| Entité | Se déclenche |
|--------|-------------|
| `binary_sensor.sortir_collecte_volumineux_sur_inscription_stcesaire` | 12h avant la collecte des volumineux |
| `binary_sensor.sortir_recuperation_stcesaire` | 12h avant la récupération |
| `binary_sensor.sortir_ordures_menageres_residuelles_stcesaire` | 12h avant les ordures ménagères |
| `binary_sensor.sortir_collecte_de_pellicules_agricoles_stcesaire` | 12h avant les pellicules agricoles |
| `binary_sensor.sortir_collecte_residus_verts_stcesaire` | 12h avant les résidus verts |
| `binary_sensor.sortir_collecte_compost_dechets_alimentaires_stcesaire` | 12h avant le compost / déchets alimentaires |
| `binary_sensor.sortir_collecte_de_branches_sur_inscription_stcesaire` | 12h avant la collecte de branches |

**Attributs** : `message`, `prochaine_collecte`, `jours_restants`, `activation_a_partir_de`

#### Rappels d'inscription — actifs de J-21 à J-8 avant la collecte

| Entité | Se déclenche |
|--------|-------------|
| `binary_sensor.inscrire_collecte_volumineux_stcesaire` | Entre 21 et 8 jours avant la collecte des volumineux |
| `binary_sensor.inscrire_collecte_branches_stcesaire` | Entre 21 et 8 jours avant la collecte de branches |

**Attributs** : `message`, `prochaine_collecte`, `jours_restants`, `inscription_debut`, `inscription_fin`

---

## Installation

### Via HACS (recommandé)
1. HACS → Intégrations → ⋮ → Dépôts personnalisés
2. Ajouter l'URL du dépôt GitHub, catégorie **Integration**

[![Ouvrir dans HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=alray31&repository=collecte_rouville&category=integration)

3. Installer l'intégration **Collecte MRC de Rouville** dans HACS et redémarrer HA
4. **Paramètres → Appareils et Services → + Ajouter une intégration → Collecte MRC de Rouville**
5. Choisir votre ville dans la liste déroulante

### Manuel
1. Copier `custom_components/collecte_rouville/` dans `config/custom_components/`
2. Redémarrer Home Assistant
3. **Paramètres → Appareils et Services → + Ajouter une intégration → Collecte MRC de Rouville**
4. Choisir votre ville dans la liste déroulante

---

## Exemples d'automatisations

### Notification quand il faut sortir les bacs
```yaml
automation:
  - alias: "Rappel sortir les bacs"
    trigger:
      - platform: state
        entity_id:
          - binary_sensor.sortir_ordures_menageres_residuelles_stcesaire
          - binary_sensor.sortir_collecte_compost_dechets_alimentaires_stcesaire
          - binary_sensor.sortir_collecte_residus_verts_stcesaire
        to: "on"
    action:
      - service: notify.mobile_app_mon_telephone
        data:
          title: "🗑️ Collecte demain !"
          message: "{{ trigger.to_state.attributes.message }}"
```

### Notification pour s'inscrire à une collecte sur inscription
```yaml
automation:
  - alias: "Rappel inscription collecte volumineux"
    trigger:
      - platform: state
        entity_id: binary_sensor.inscrire_collecte_volumineux_stcesaire
        to: "on"
    action:
      - service: notify.mobile_app_mon_telephone
        data:
          title: "📋 Inscription requise"
          message: "{{ trigger.to_state.attributes.message }}"
```

### Carte Lovelace
```yaml
type: entities
title: 🗑️ Collectes – St-Césaire
entities:
  - entity: binary_sensor.sortir_ordures_menageres_residuelles_stcesaire
    name: "Sortir les ordures ?"
  - entity: sensor.ordures_menageres_residuelles_stcesaire
    name: "Prochaine date — Ordures"
  - entity: binary_sensor.sortir_recuperation_stcesaire
    name: "Sortir la récupération ?"
  - entity: sensor.recuperation_stcesaire
    name: "Prochaine date — Récupération"
  - entity: binary_sensor.sortir_collecte_compost_dechets_alimentaires_stcesaire
    name: "Sortir le compost ?"
  - entity: sensor.collecte_compost_dechets_alimentaires_stcesaire
    name: "Prochaine date — Compost"
  - entity: binary_sensor.sortir_collecte_residus_verts_stcesaire
    name: "Sortir les résidus verts ?"
  - entity: sensor.collecte_residus_verts_stcesaire
    name: "Prochaine date — Résidus verts"
  - entity: binary_sensor.inscrire_collecte_volumineux_stcesaire
    name: "S'inscrire — Volumineux ?"
  - entity: sensor.collecte_volumineux_sur_inscription_stcesaire
    name: "Prochaine date — Volumineux"
  - entity: binary_sensor.inscrire_collecte_branches_stcesaire
    name: "S'inscrire — Branches ?"
  - entity: sensor.collecte_de_branches_sur_inscription_stcesaire
    name: "Prochaine date — Branches"
```

---

## ⚠️ Avis de non-affiliation

Cette intégration est un projet communautaire indépendant et n'est **ni développée, ni approuvée, ni affiliée à la MRC de Rouville, à ses municipalités membres, ni à Publidata**.

Les données de collecte proviennent des calendriers ICS publics mis à disposition par Publidata pour le compte des municipalités. L'exactitude et la disponibilité de ces données relèvent entièrement de ces organismes.

Pour toute question, problème ou suggestion concernant **cette intégration**, veuillez ouvrir un ticket via le système de suivi GitHub :

👉 **[Ouvrir un ticket (GitHub Issues)](https://github.com/alray31/collecte_rouville/issues)**

Veuillez **ne pas contacter la MRC de Rouville ni ses municipalités** pour obtenir du support relatif à cette intégration.

---

## 📄 Licence

Ce projet est distribué sous licence **MIT**. Voir le fichier [`LICENSE`](LICENSE) pour les détails.
