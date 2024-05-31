#!/bin/bash

echo 'export AES_KEY="${AES_KEY}"' >> ~/.profile
echo 'export HMAC_KEY="${HMAC_KEY}"' >> ~/.profile
echo 'export IV="${IV}"' >> ~/.profile

git clone git@github.com:arquisoft-genesis-202401/sprint-4-final.git

cd sprint-4-final/crypto_module

envsubst < Dockerfile > Dockerfile.envsubst

sudo docker build -t crypto_module -f Dockerfile.envsubst .

# Run the Docker container
sudo docker run -d -p 8080:8080 --name crypto_module \
  -e AES_KEY=${AES_KEY} \
  -e HMAC_KEY=${HMAC_KEY} \
  -e IV=${IV} \
  crypto_module
