#!/bin/bash

export AES_KEY="${AES_KEY}"
export HMAC_KEY="${HMAC_KEY}"
export IV="${IV}"

git https://github.com/arquisoft-genesis-202401/sprint-4-final.git

cd sprint-4-final/crypto_module

sudo docker build -t crypto_module .

# Run the Docker container
sudo docker run -d -p 8080:8080 --name crypto_module \
  -e AES_KEY=$AES_KEY \
  -e HMAC_KEY=$HMAC_KEY \
  -e IV=$IV \
  crypto_module
