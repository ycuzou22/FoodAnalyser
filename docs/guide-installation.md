# Guide d'installation (développement local)

## 1. Prérequis

- Les outils listés dans le [README](../README.md#prérequis)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows / macOS) ou Docker Engine + plugin Compose v2 (Linux)

## 2. Premier lancement

```bash
make install                                      # dépendances + hooks Git
cp infra/docker/.env.example infra/docker/.env    # puis changer les mots de passe
make up
```

`make up` construit l'image de l'API, démarre tous les services et attend qu'ils soient sains (`--wait`). Au premier lancement, compter 1 à 2 minutes (téléchargement des images).

Vérification :

```bash
curl http://localhost:8000/health   # {"status":"ok"}
curl http://localhost:8000/ready    # {"status":"ready","checks":{"database":"ok","redis":"ok","rabbitmq":"ok"}}
```

## 3. Services

| Service | Rôle | Accès depuis la machine | Identifiants |
| --- | --- | --- | --- |
| `api` | API FastAPI, rechargement à chaud | http://localhost:8000 (docs : `/docs`) | — |
| `postgres` | Base de données | `localhost:5432` | `POSTGRES_*` du `.env` |
| `redis` | Cache, quotas, limitation de débit | `localhost:6379` | sans mot de passe (local uniquement) |
| `rabbitmq` | File des analyses photo | `localhost:5672`, console http://localhost:15672 | `RABBITMQ_*` du `.env` |
| `minio` | Stockage objet compatible S3 | API `localhost:9000`, console http://localhost:9001 | `MINIO_ROOT_*` du `.env` |
| `minio-init` | Crée le bucket `meal-photos` (privé, versionné) puis s'arrête | — | — |

Tous les ports sont publiés sur `127.0.0.1` uniquement. Pour changer un port déjà pris, modifier la variable `*_PORT` correspondante dans `infra/docker/.env`.

## 4. Commandes

| Commande | Effet |
| --- | --- |
| `make up` | Démarre (ou met à jour) l'environnement |
| `make down` | Arrête tout, données conservées |
| `make logs` / `make logs s=api` | Suit les logs |
| `make ps` | État des conteneurs |
| `make reset-db` | Supprime le volume PostgreSQL et repart d'une base vide |

## 5. Développer l'API

Le dossier `services/api/app` est monté dans le conteneur : toute modification est rechargée automatiquement. Pour lancer l'API hors Docker (débogueur de l'IDE) :

```bash
cd services/api
cp .env.example .env      # mêmes mots de passe que infra/docker/.env
uv run uvicorn app.main:app --reload
```

## 6. Sécurité

- Les fichiers `.env` ne sont jamais commités (`.gitignore`) ; le Compose refuse de démarrer si une variable obligatoire manque.
- Les conteneurs de l'API tournent avec un utilisateur non-root (`uid 10001`).
- Le bucket MinIO n'autorise aucun accès anonyme.

## 7. Dépannage

| Symptôme | Cause probable | Solution |
| --- | --- | --- |
| `required variable … is missing a value` | `infra/docker/.env` absent ou incomplet | `cp infra/docker/.env.example infra/docker/.env` |
| `port is already allocated` | Un PostgreSQL / Redis local tourne déjà | Changer le port dans `infra/docker/.env` |
| `/ready` renvoie 503 | Un service n'est pas encore prêt | `make ps`, puis `make logs s=<service>` |
| Les mots de passe changés ne sont pas pris en compte | PostgreSQL et RabbitMQ gardent ceux de leur premier démarrage | `make down`, supprimer les volumes (`docker volume rm foodanalyser_pg-data foodanalyser_rabbitmq-data`), `make up` |
