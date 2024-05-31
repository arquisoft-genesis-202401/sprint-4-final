#!/bin/bash
sudo apt-get update
sudo apt-get install -y postgresql postgresql-contrib
sudo -u postgres psql -c "CREATE USER ${POSTGRESQL_DB_USER} WITH PASSWORD '${POSTGRESQL_DB_PASSWORD}';"
sudo -u postgres createdb -O ${POSTGRESQL_DB_USER} ${POSTGRESQL_DB_NAME}
echo "host all all ${INTERFACE_USER_DATABASE} trust" | sudo tee -a /etc/postgresql/12/main/pg_hba.conf
echo "listen_addresses='${LISTEN_ADDR_USER_DATABASE}'" | sudo tee -a /etc/postgresql/12/main/postgresql.conf
echo "max_connections=${MAX_CONN_USER_DATABASE}" | sudo tee -a /etc/postgresql/12/main/postgresql.conf
sudo sed -i 's/local   all             all                                     peer/local   all             all                                     md5/' /etc/postgresql/12/main/pg_hba.conf
sudo service postgresql restart
echo "Done"