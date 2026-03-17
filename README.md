[![Stars](https://img.shields.io/github/stars/alray31/collecte_rouville?style=for-the-badge)](#) [![Last commit](https://img.shields.io/github/last-commit/alray31/collecte_rouville?style=for-the-badge)](#)

[![HACS Default][hacs_shield]][hacs]
[![GitHub Latest Release][releases_shield]][latest_release]

[hacs_shield]: https://img.shields.io/static/v1.svg?label=HACS&message=Default&style=popout&color=green&labelColor=41bdf5&logo=HomeAssistantCommunityStore&logoColor=white
[hacs]: https://hacs.xyz/docs/default_repositories

[latest_release]: https://github.com/alray31/collecte_rouville/releases/latest
[releases_shield]: https://img.shields.io/github/release/alray31/collecte_rouville


[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.me/AlainRaymond564)

# 🗑️♻️ Collecte MRC de Rouville — Intégration HACS Home Assistant

🗑️ Intégration HACS Home Assistant pour les collectes municipales de la MRC de Rouville — capteurs de dates et alertes automatiques.

![Icon](https://github.com/user-attachments/assets/ca0dd53e-06a3-4fa9-ba99-162ad82b7471?raw=true)


[![Ouvrir dans HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=alray31&repository=collecte_rouville&category=integration)

---

## Municipalités supportées

- Ange-Gardien
- Marieville
- Richelieu
- Rougemont
- Saint-Césaire
- Saint-Mathias-sur-Richelieu
- Saint-Paul-d'Abbotsford
- Sainte-Angèle-de-Monnoir

---

## Installation via HACS

1. Dans HACS, allez dans **Intégrations** → menu ⋮ → **Dépôts personnalisés**
2. Ajoutez `https://github.com/alray31/collecte_rouville` avec la catégorie **Intégration**
3. Installez **Collecte MRC de Rouville**
4. Redémarrez Home Assistant

---

## Configuration

1. Allez dans **Paramètres → Appareils & Services → Ajouter une intégration**
2. Recherchez **Collecte MRC de Rouville**
3. Choisissez votre municipalité
4. Entrez votre adresse

> 💡 Consultez le [widget Publidata de votre ville](https://widget.publidata.ca/NKx0JtQVX3/) pour voir le format d'adresse attendu avant de configurer l'intégration.

---

## Entités créées

Toutes les entités sont regroupées dans un appareil nommé **Collecte {votre ville}**.

### Capteurs de collecte (7)

| Entité | Description | État |
|--------|-------------|------|
| `sensor.ordures_menageres` | Ordures ménagères résiduelles | "Aujourd'hui" / "Demain" / "Dans X jours" |
| `sensor.recuperation` | Collecte sélective | idem |
| `sensor.residus_alimentaires` | Résidus alimentaires | idem |
| `sensor.residus_verts` | Déchets végétaux | idem |
| `sensor.volumineux` | Encombrants | idem |
| `sensor.branches` | Branches et bois | idem |
| `sensor.pellicules_agricoles` | Plastiques agricoles | idem |

**Attributs disponibles :** `prochaine_date`, `jours_restants`, `dates_futures`, `service_name`, `adresse`, `ville`

### Capteurs binaires "sortir" (7)

Actifs 12 heures avant la collecte jusqu'au lendemain soir. Utiles pour déclencher des notifications ou des automatisations.

### Capteurs binaires "inscription" (2)

Pour les collectes **Volumineux** et **Branches** qui nécessitent une inscription préalable. Actifs entre J-21 et J-8 avant la collecte.

### Écocentres (4)

| Entité | Description |
|--------|-------------|
| `binary_sensor.ecocentre_de_marieville` | Ouvert / Fermé en ce moment |
| `sensor.ecocentre_de_marieville_prochaine_ouverture` | Prochaine ouverture (ex: "Demain à 09:00") |
| `binary_sensor.ecocentre_de_saint_cesaire` | Ouvert / Fermé en ce moment |
| `sensor.ecocentre_de_saint_cesaire_prochaine_ouverture` | Prochaine ouverture |

> Les écocentres sont communs à toute la MRC — ils apparaissent pour toutes les villes configurées.

<img width="304" height="1017" alt="image" src="https://github.com/user-attachments/assets/24add360-c818-4c16-91cf-2b5aa1ef0c46" />


---

## Exemple d'automatisation

```yaml
automation:
  - alias: "Notification collecte ordures"
    trigger:
      - platform: state
        entity_id: binary_sensor.sortir_ordures_menageres
        to: "on"
    action:
      - service: notify.mobile_app
        data:
          message: "🗑️ Sortir les ordures ce soir !"
```

---

## Données

Les données proviennent de l'API REST Publidata utilisée par le widget officiel de la MRC de Rouville. Elles sont actualisées toutes les heures.

---

## Licence

MIT — Voir [LICENSE](LICENSE)
