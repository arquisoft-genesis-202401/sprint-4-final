#!/bin/bash

# Export environment variables
export PRIVATE_IP_USER_DATABASE="${PRIVATE_IP_USER_DATABASE}"
export PORT_USER_DATABASE="${PORT_USER_DATABASE}"
export POSTGRESQL_DB_NAME="${POSTGRESQL_DB_NAME}"
export POSTGRESQL_DB_USER="${POSTGRESQL_DB_USER}"
export POSTGRESQL_DB_PASSWORD="${POSTGRESQL_DB_PASSWORD}"
export PRIVATE_IP_CRYPTO_MANAGER="${PRIVATE_IP_CRYPTO_MANAGER}"

# Clone the repository
git clone https://github.com/arquisoft-genesis-202401/sprint-4-final.git
cd sprint-4-final/user_manager/

# Build the Docker image
sudo docker build -t user_manager .

# Run the Docker container
sudo docker run -d -p 8000:8000 --name user_manager \
  -e PRIVATE_IP_USER_DATABASE=$PRIVATE_IP_USER_DATABASE \
  -e PORT_USER_DATABASE=$PORT_USER_DATABASE \
  -e POSTGRESQL_DB_NAME=$POSTGRESQL_DB_NAME \
  -e POSTGRESQL_DB_USER=$POSTGRESQL_DB_USER \
  -e POSTGRESQL_DB_PASSWORD=$POSTGRESQL_DB_PASSWORD \
  user_manager
