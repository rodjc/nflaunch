# Google Cloud Platform Setup

This guide covers the GCP permissions, IAM roles, and authentication required to use `nflaunch` with Google Cloud Batch.

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

## Environment Variables

`nflaunch` supports environment variables to reduce repetitive command-line arguments for Google Cloud configuration. These variables are particularly useful for setting up project-wide or team-wide defaults.

### Supported Environment Variables

| Environment Variable | CLI Equivalent | Description | Example Value |
|---------------------|----------------|-------------|---------------|
| `NFL_GCP_PROJECT_ID` | `--project-id` | Google Cloud project ID | `my-project-123` |
| `NFL_GCP_REGION` | `--region` | Google Cloud region for Batch jobs | `europe-west4` |
| `NFL_GCP_SERVICE_ACCOUNT` | `--service-account-email` | Service account email for Batch and GCS | `nflaunch-runner@my-project.iam.gserviceaccount.com` |
| `NFL_GCP_NETWORK` | `--network` | VPC network name | `projects/my-project/global/networks/my-vpc` |
| `NFL_GCP_SUBNETWORK` | `--subnetwork` | Subnetwork name | `projects/my-project/regions/europe-west4/subnetworks/my-subnet` |
| `NFL_GCP_BASE_BUCKET` | `--base-bucket` | Base GCS bucket for configs, logs, cache | `gs://my-nflaunch-bucket` or `my-nflaunch-bucket` |

### Precedence Rules

**Command-line arguments always override environment variables.** This allows you to set defaults via environment variables while maintaining the flexibility to override them on a per-run basis.

For example:
```bash
# Set default region
export NFL_GCP_REGION="europe-west4"

# This run uses europe-west4
nflaunch --pipeline-name nf-core/rnaseq ...

# This run overrides to use europe-west1
nflaunch --region europe-west1 --pipeline-name nf-core/rnaseq ...
```

### Example Configuration

Add to `~/.bashrc` or `~/.bash_profile`
```bash
# nflaunch GCP configuration
export NFL_GCP_PROJECT_ID="my-project-123"
export NFL_GCP_REGION="europe-west4"
export NFL_GCP_SERVICE_ACCOUNT="nflaunch-runner@my-project-123.iam.gserviceaccount.com"
export NFL_GCP_NETWORK="projects/my-project-123/global/networks/shared-vpc"
export NFL_GCP_SUBNETWORK="projects/my-project-123/regions/europe-west4/subnetworks/default"
export NFL_GCP_BASE_BUCKET="gs://my-org-nflaunch"
```

To apply immediately in your current session, run the export commands in your terminal.

### Verifying Configuration

Check which environment variables are set:

```bash
env | grep NFL_GCP
```

### Benefits

Using environment variables provides several advantages:

- **Reduced command-line verbosity** - No need to repeat infrastructure settings for each run
- **Team standardization** - Enforce consistent GCP settings across team members
- **Environment-specific configs** - Easily switch between dev, staging, and production setups

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

### Check Permissions

```bash
gcloud projects get-iam-policy YOUR_PROJECT \
  --flatten="bindings[].members" \
  --filter="bindings.members:YOUR_SA@PROJECT.iam.gserviceaccount.com" \
  --format="table(bindings.role)"
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
5. **Aaudit logs** - Track Batch job submissions and modifications

## Next Steps

After completing GCP setup:

- Return to [Installation Guide](installation.md) if not yet installed
- Proceed to [Quickstart Guide](quickstart.md) to run your first pipeline
- Review [CLI Reference](cli-reference.md) for all available options
