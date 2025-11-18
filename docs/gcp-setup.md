# Google Cloud Platform Setup

This guide covers the GCP permissions, IAM roles, and authentication required to use`nflaunch`with Google Cloud Batch.

## Required APIs

Enable the following APIs in your target GCP project:

- **Batch API** (`batch.googleapis.com`)
- **Cloud Storage API** (`storage.googleapis.com`)

You can enable these via the Cloud Console or using `gcloud`:

### Using gcloud CLI

```bash
gcloud services enable batch.googleapis.com storage.googleapis.com --project=YOUR_PROJECT_ID
```

### Using Cloud Console

1. Navigate to [APIs & Services > Library](https://console.cloud.google.com/apis/library)
2. Search for and enable:
    - **Batch API**
    - **Cloud Storage API**


## IAM Permissions

### User IAM Roles

The **user** running `nflaunch` should have the following IAM roles in the GCP project:

- `roles/batch.jobEditor` - Create and manage Batch jobs
- `roles/storage.objectAdmin` - Full control over Cloud Storage objects
  - Alternatively, use a combination of:
    - `roles/storage.objectCreator`
    - `roles/storage.objectViewer`
    - `roles/storage.objectLister`
- `roles/iam.serviceAccountUser` - Act as the Batch runner service account

### Service Account IAM Roles

The **service account** used to run Batch jobs should have:

- `roles/batch.agentReporter` - Report job status to Batch API
- `roles/batch.jobEditor` - Create and manage Batch jobs
- `roles/logging.logWriter` - Write logs to Cloud Logging
- `roles/logging.viewer` - Read logs from Cloud Logging
- `roles/storage.objectUser` - Read and write Cloud Storage objects
- `roles/iam.serviceAccountUser` - Act as itself for job execution

## Authentication

Before running `nflaunch`, authenticate locally:

### User Credentials

```bash
gcloud auth login
```

### Application Default Credentials

Required for API calls made by `nflaunch`:

```bash
gcloud auth application-default login
```

### Set Default Project

Set your default project to avoid conflicts with other projects:

```bash
gcloud config set project YOUR_PROJECT_ID
```

## Service Account Creation

If you need to create a new service account for Batch jobs:

```bash
# Create service account
gcloud iam service-accounts create nflaunch-runner \
  --display-name="nflaunch Batch Runner" \
  --project=YOUR_PROJECT_ID

# Grant required roles
for role in batch.agentReporter batch.jobEditor logging.logWriter logging.viewer storage.objectUser iam.serviceAccountUser; do
  gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:nflaunch-runner@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/$role"
done
```

## Verifying Setup

Before running nflaunch, verify your setup:

### Check Authentication

```bash
gcloud auth list
gcloud auth application-default print-access-token
```

### Verify Permissions

```bash
# Test Batch API access
gcloud batch jobs list --project=YOUR_PROJECT_ID --location=YOUR_REGION

# Test Storage access
gsutil ls gs://YOUR_BUCKET/
```

### Check Enabled APIs

```bash
gcloud services list --enabled --project=YOUR_PROJECT_ID | grep -E 'batch|storage'
```

## Troubleshooting

### Permission Denied Errors

If you receive permission denied errors:

1. Verify your user has the required IAM roles
2. Ensure Application Default Credentials are set
3. Check the service account has appropriate roles
4. Verify APIs are enabled

### Network Errors

If jobs fail with network connectivity issues:

1. Verify Private Google Access is enabled on your subnetwork
2. Check firewall rules allow required egress traffic
3. Ensure the subnetwork exists in the specified region

### Service Account Issues

If the service account cannot be used:

1. Verify the service account exists: `gcloud iam service-accounts list`
2. Check you have `roles/iam.serviceAccountUser` permission
3. Ensure the service account email is correctly specified with `--service-account-email`

## Security Best Practices

1. **Use separate service accounts** - Don't use your personal account for Batch jobs
2. **Apply least privilege** - Grant only the minimum required permissions
3. **Audit regularly** - Review IAM policies and service account usage
4. **Use organization policies** - Enforce constraints on resource usage
5. **Enable audit logs** - Track Batch job submissions and modifications

## Next Steps

After completing GCP setup:

- Return to [Installation Guide](installation.md) if not yet installed
- Proceed to [Quickstart Guide](quickstart.md) to run your first pipeline
- Review [CLI Reference](cli-reference.md) for all available options
