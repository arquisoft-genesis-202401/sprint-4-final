# Sprint 4 Final

## Overview
This document outlines the steps for deploying Sprint 3 Final using Python 3.12

## Deployment Instructions

### Step 1: Set Up Your GCP Project
Before you begin, you need to create a Google Cloud Platform (GCP) project if you don't already have one. This project will house all the resources required for our application.

- **Create a Project:**
  - Go to the [Google Cloud Console](https://console.cloud.google.com/).
  - Click on the project dropdown near the top of the dashboard.
  - Click on ‘New Project’ and follow the prompts to create a new project.

### Step 2: Configure Keyring and Keys
After setting up your GCP project, create your encryption keys to handle encryption operations securely.

- **Create Encryption Key for Symmetric Encryption:**
  - Configure the key with the following specifications:
    - Algorithm: AES-256
    - Mode: CBC
    - Padding: PKCS5Padding
    - Key length: 256 bits

- **Create IV for Symmetric Encryption:**
  - Randomly-securely generated 16-byte vector

- **Create a Key for HMAC Calculation:**
  - Configure the key as follows:
    - Algorithm: HMAC-SHA256
    - Key length: 256 bits

### Step 3: Integrate with User Manager
Ensure that your `user_manager` component is properly configured to fetch encryption keys from your ENV VARS (set_env_vars.sh file) and to manage encryption, decryption, and HMAC calculations effectively.


### Step 4: Download and Configure Templates
- Download the necessary templates:
    ```bash
    wget --no-cache https://raw.githubusercontent.com/arquisoft-genesis-202401/sprint-4-final/main/set_env_vars.sh.template
    wget --no-cache https://raw.githubusercontent.com/arquisoft-genesis-202401/sprint-4-final/main/deployment.yaml.template
    ```

- Update `set_env_vars.sh.template` with the real values and save it as `set_env_vars.sh`.

- Grant execution permission to the script:
    ```bash
    chmod +x set_env_vars.sh
    ```

- Source the environment variables:
    ```bash
    source set_env_vars.sh
    ```

### Step 5: Create and Manage Deployment
- Create the deployment using `gcloud deployment-manager`:
    ```bash
    gcloud deployment-manager deployments create sprint-4-final-deployment --config deployment.yaml
    ```

- To delete the deployment, run:
    ```bash
    gcloud deployment-manager deployments delete sprint-4-final-deployment
    ```

- To update the deployment configuration, use:
    ```bash
    gcloud deployment-manager deployments update sprint-4-final-deployment --config deployment.yaml
    ```

## Additional Steps (Optional)
- View startup logs using:
    ```bash
    sudo journalctl -u google-startup-scripts.service
    ```
- Log in into the business database:
    ```bash
    psql -U <db_user> -d <db_name> --password
    ```
