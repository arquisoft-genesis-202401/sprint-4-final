FROM python:3.12-alpine

WORKDIR /app

# Copy the django app to the working directory
COPY . /app

# Set the environment variables
ENV PRIVATE_IP_USER_DATABASE 0
ENV PORT_USER_DATABASE 0
ENV POSTGRESQL_DB_NAME 0
ENV POSTGRESQL_DB_USER 0
ENV POSTGRESQL_DB_PASSWORD 0
ENV PRIVATE_IP_CRYPTO_MANAGER 0
ENV PRIVATE_IP_AUTH_MANAGER 0

# Install Python dependencies
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["sh", "init.sh"]