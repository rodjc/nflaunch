#!/bin/bash

# Set environment variables
export NFL_GCP_PROJECT_ID="YOUR_PROJECT_ID"
export NFL_GCP_REGION="YOUR_REGION"
export NFL_GCP_SERVICE_ACCOUNT="YOUR_SERVICE_ACCOUNT_EMAIL"
export NFL_GCP_NETWORK="YOUR_NETWORK_RESOURCE_NAME"
export NFL_GCP_SUBNETWORK="YOUR_SUBNETWORK_RESOURCE_NAME"
export NFL_GCP_BASE_BUCKET="YOUR_BASE_BUCKET"

nflaunch \
  --pipeline-name nf-core/demo \
  --pipeline-version 1.0.2 \
  --profile docker \
  --params-file params.yaml \
  --samplesheet samplesheet.csv \
  --config-file resources.config \
  --dry-run
