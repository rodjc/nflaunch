#!/bin/bash

# TODO: Replace the dummy values below with your actual config values before running the script.
BASE_BUCKET="YOUR_BASE_BUCKET"
PROJECT_ID="YOUR_PROJECT_ID"
REGION="YOUR_REGION"
SERVICE_ACCOUNT_EMAIL="YOUR_SERVICE_ACCOUNT_EMAIL"
NETWORK_RESOURCE_NAME="YOUR_NETWORK_RESOURCE_NAME"
SUBNETWORK_RESOURCE_NAME="YOUR_SUBNETWORK_RESOURCE_NAME"

nflaunch \
  --pipeline-name nf-core/demo \
  --pipeline-version 1.0.2 \
  --profile docker \
  --params-file params.yaml \
  --samplesheet samplesheet.csv \
  --config-file resources.config \
  --base-bucket "$BASE_BUCKET" \
  --project-id "$PROJECT_ID" \
  --region "$REGION" \
  --service-account-email "$SERVICE_ACCOUNT_EMAIL" \
  --network "$NETWORK_RESOURCE_NAME" \
  --subnetwork "$SUBNETWORK_RESOURCE_NAME" \
  --dry-run
