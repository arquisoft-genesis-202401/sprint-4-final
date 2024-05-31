#!/bin/bash
cd ~
echo 'export PRIVATE_IP_BUSINESS_DATABASE="${PRIVATE_IP_BUSINESS_DATABASE}"' >> ~/.profile
echo 'export PORT_BUSINESS_DATABASE="${PORT_BUSINESS_DATABASE}"' >> ~/.profile
echo 'export POSTGRESQL_DB_NAME="${POSTGRESQL_DB_NAME}"' >> ~/.profile
echo 'export POSTGRESQL_DB_USER="${POSTGRESQL_DB_USER}"' >> ~/.profile
echo 'export POSTGRESQL_DB_PASSWORD="${POSTGRESQL_DB_PASSWORD}"' >> ~/.profile
echo 'export ACCOUNT_SID="${ACCOUNT_SID}"' >> ~/.profile
echo 'export AUTH_TOKEN="${AUTH_TOKEN}"' >> ~/.profile
echo 'export SERVICE_SID="${SERVICE_SID}"' >> ~/.profile
source ~/.profile
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install python3.12 -y
git clone https://github.com/arquisoft-genesis-202401/sprint-3-final.git
cd sprint-3-final/
python3.12 -m venv env --without-pip
source env/bin/activate
curl https://bootstrap.pypa.io/get-pip.py | python
pip install -r requirements.txt
cd user_manager/
until nc -z ${PRIVATE_IP_BUSINESS_DATABASE} ${PORT_BUSINESS_DATABASE}; do
  echo "Waiting for business database to be reachable..."
  sleep 10
done
echo "Business database is up and running."
python manage.py makemigrations user_manager
python manage.py migrate user_manager
python manage.py runserver ${INTERFACE_2_USER_MANAGER}:${PORT_USER_MANAGER}