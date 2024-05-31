#!/bin/bash

# Export environment variables
export ACCOUNT_SID="${ACCOUNT_SID}"
export AUTH_TOKEN="${AUTH_TOKEN}"
export SERVICE_SID="${SERVICE_SID}"
export PRIVATE_IP_CRYPTO_MANAGER="${PRIVATE_IP_CRYPTO_MANAGER}"

# Clone the repository
git clone https://github.com/arquisoft-genesis-202401/sprint-4-final.git
cd sprint-4-final/auth_manager/

# Build the Docker image
sudo docker build -t auth_manager .

# Run the Docker container
sudo docker run -d -p 8080:8080 --name auth_manager \
  -e ACCOUNT_SID=$ACCOUNT_SID \
  -e AUTH_TOKEN=$AUTH_TOKEN \
  -e SERVICE_SID=$SERVICE_SID \
  -e SERVICE_SID=$PRIVATE_IP_CRYPTO_MANAGER \
  auth_manager
