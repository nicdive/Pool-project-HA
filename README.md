# Pool Project HA

Récupération de données et actionneurs piscine vers Home Assistant.

## Phase 1 — Actionneurs HTTP (Arduino)

Intégration custom **`pool_http_actuators`** : pilote le petit serveur web Arduino via **HTTP GET** (même principe qu’eedomus).  
La barrette relais Ethernet remplacera ça ensuite ; cette intégration reste utilisable en parallèle si besoin.

### Compatible avec ton sketch

| Action | Requête envoyée |
|--------|-----------------|
| On (`ouvre`) | `GET http://<IP>/ouvre` → `RELAY2 = LOW` |
| Off (`ferme`) | `GET http://<IP>/ferme` → `RELAY2 = HIGH` |

Pas de `/status` côté Arduino → l’état du switch HA est **optimiste**.

### Installation

1. Copier le dossier `custom_components/pool_http_actuators` dans  
   `/config/custom_components/` de Home Assistant.
2. Redémarrer Home Assistant.
3. **Paramètres → Appareils et services → Ajouter une intégration**  
   → **Pool HTTP Actuators**.
4. Saisir l’IP du module (ex. `192.168.24.142` ou celle vue dans eedomus).
5. Ouvrir l’intégration → **Configurer** → **Ajouter un actionneur** :
   - **Nom** : `Cascade Piscine`
   - **Chaîne ON** : `ouvre`
   - **Chaîne OFF** : `ferme`

Pour d’autres relais sur le même Arduino (si tu ajoutes des routes), répéter l’ajout avec d’autres chaînes.  
Pour un autre IP, ajouter une 2ᵉ instance de l’intégration.

### Structure

```
custom_components/pool_http_actuators/
  __init__.py
  config_flow.py
  const.py
  http_client.py
  switch.py
  manifest.json
  strings.json
  translations/
```
