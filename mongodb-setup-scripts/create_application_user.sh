#!/usr/bin/env sh
echo "Creating an application user."

file_env "MONGO_DATABASE_USERNAME"
file_env "MONGO_DATABASE_PASSWORD"

mongo "$MONGO_INITDB_DATABASE" \
  -u "$MONGO_INITDB_ROOT_USERNAME" \
  -p "$MONGO_INITDB_ROOT_PASSWORD" \
  --authenticationDatabase admin \
  --eval "db.createUser({ \
                          user: $(_js_escape "$MONGO_DATABASE_USERNAME"), \
                          pwd: $(_js_escape "$MONGO_DATABASE_PASSWORD"), \
                          roles:[{ role: 'readWrite', db: $(_js_escape "$MONGO_INITDB_DATABASE") }], \
                          mechanisms: ['SCRAM-SHA-256'] \
                       })"
