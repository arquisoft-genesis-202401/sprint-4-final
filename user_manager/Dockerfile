FROM python:3.12-alpine

WORKDIR /app

# Copy the django app to the working directory
COPY . /app

# Set the environment variables
ENV VARIABLES_DB_HOST ${PRIVATE_IP_USER_MANAGER}
ENV PRIVATE_IP_USER_DATABASE ${PRIVATE_IP_USER_DATABASE}
ENV PORT_USER_DATABASE ${PORT_USER_DATABASE}
ENV POSTGRESQL_DB_NAME ${POSTGRESQL_DB_NAME}
ENV POSTGRESQL_DB_USER ${POSTGRESQL_DB_USER}
ENV POSTGRESQL_DB_PASSWORD ${POSTGRESQL_DB_PASSWORD}
ENV PRIVATE_IP_CRYPTO_MANAGER ${PRIVATE_IP_CRYPTO_MANAGER}

# Install Python dependencies
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["sh", "init.sh"]