# Pool Project HA

Récupération de données et actionneurs piscine vers Home Assistant.

## Intégration `pool_http_actuators`

Contrôle des actionneurs exposés par un petit serveur web (Arduino Ethernet, etc.) via **HTTP GET**, comme sous eedomus.

### Exemple (Cascade)

| État | Requête |
|------|---------|
| On   | `GET http://192.168.23.241/ouvre` |
| Off  | `GET http://192.168.23.241/ferme` |

### Installation

1. Copier `custom_components/pool_http_actuators` dans le dossier `custom_components` de Home Assistant.
2. Redémarrer Home Assistant.
3. **Paramètres → Appareils et services → Ajouter une intégration → Pool HTTP Actuators**.
4. Saisir l’IP du module (ex. `192.168.23.241`).
5. Ouvrir l’intégration → **Configurer** → **Ajouter un actionneur** :
   - Nom : `Cascade Piscine`
   - Chaîne ON : `ouvre`
   - Chaîne OFF : `ferme`

Répéter pour chaque actionneur (éclairage, pompes, etc.) sur la même IP ou sur une autre intégration si IP différente.

### État (retour)

Pour l’instant **pas de lecture d’état** côté Arduino : le switch HA utilise un **état optimiste** (il affiche ON/OFF selon la dernière commande réussie).

Dès que le sketch Arduino sera disponible, on pourra ajouter un endpoint de statut si le firmware le permet.

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
