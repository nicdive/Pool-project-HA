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

### Installation (HACS — recommandé)

Repo GitHub : **`nicdive/Pool-project-HA`**

1. HACS → **Integrations** → ⋮ → **Custom repositories**
2. Repository : `nicdive/Pool-project-HA` — Category : **Integration**
3. Installer **Pool HTTP Actuators**, puis redémarrer Home Assistant
4. **Paramètres → Appareils et services → Ajouter une intégration**  
   → **Pool HTTP Actuators**
5. Saisir l’IP du module (ex. `192.168.24.142` ou celle vue dans eedomus)
6. Ouvrir l’intégration → **Configurer** → **Ajouter un actionneur** :
   - **Nom** : `Cascade Piscine`
   - **Chaîne ON** : `ouvre`
   - **Chaîne OFF** : `ferme`

Installation manuelle possible : copier `custom_components/pool_http_actuators` dans `/config/custom_components/`.

### Versioning

- `manifest.json` → `"version": "0.1.0"`
- Release GitHub tag → `0.1.0` (obligatoire pour que HACS affiche une vraie version, pas un hash de commit)

https://github.com/nicdive/Pool-project-HA/releases/tag/0.1.0

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
