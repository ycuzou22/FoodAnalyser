#!/bin/sh
# Crée le bucket des photos de repas dans MinIO (développement local).
# Lancé par le service `minio-init` du Compose ; idempotent.
set -eu

: "${MINIO_ROOT_USER:?}"
: "${MINIO_ROOT_PASSWORD:?}"
BUCKET="${MINIO_BUCKET:-meal-photos}"

mc alias set local http://minio:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD" >/dev/null

mc mb --ignore-existing "local/$BUCKET"

# Bucket strictement privé : aucun accès anonyme. Les photos ne seront servies
# qu'au travers d'URL pré-signées à courte durée (issue #20).
mc anonymous set none "local/$BUCKET"

# Versionnage activé : une photo écrasée par erreur reste récupérable.
mc version enable "local/$BUCKET"

echo "Bucket « $BUCKET » prêt (privé, versionné)."
