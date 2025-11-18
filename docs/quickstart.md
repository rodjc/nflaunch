# Quickstart Guide

This guide will help you run your first Nextflow pipeline with`nflaunch`on Google Cloud Batch.

## Before You Begin

Ensure you have completed:

1. **[Installation](installation.md)** -`nflaunch`is installed and available
2. **[GCP Setup](gcp-setup.md)** - Required permissions and authentication configured

## Gather Required Information

Before getting started, collect the following from your GCP environment:

- **BASE_BUCKET** - GCS bucket for storing pipeline data (e.g., `my-nextflow-bucket`)
- **PROJECT_ID** - Google Cloud project ID
- **REGION** - Google Cloud region (e.g., `europe-west4`)
- **SERVICE_ACCOUNT** - Service account email for running batch jobs
- **NETWORK** - VPC network name (e.g., `projects/my-project/global/networks/my-vpc`)
- **SUBNETWORK** - Subnetwork name (e.g., `projects/my-project/regions/europe-west4/subnetworks/my-subnet`)

## Run a Public Nextflow Pipeline

Test your environment by running the [nf-core/demo](https://nf-co.re/demo/1.0.2) pipeline.

Sample configuration files live under `examples/` in the repository:
- `params.yaml` - Pipeline parameters
- `resources.config` - Resource configuration
- `samplesheet.csv` - Sample input data
- `run_demo.sh` - Helper script

### Dry Run (Validation)

First, validate your configuration without submitting the job:

```bash
nflaunch \
  --base-bucket BASE_BUCKET \
  --pipeline-name nf-core/demo \
  --pipeline-version 1.0.2 \
  --params-file examples/params.yaml \
  --samplesheet examples/samplesheet.csv \
  --config-file examples/resources.config \
  --project-id PROJECT_ID \
  --region REGION \
  --service-account-email SERVICE_ACCOUNT \
  --network NETWORK \
  --subnetwork SUBNETWORK \
  --labels '{"env": "test", "tool": "nflaunch"}' \
  --dry-run
```

**Important:** Replace the placeholder values (`BASE_BUCKET`, `PROJECT_ID`, etc.) with your actual GCP configuration.

### Validating the Job Configuration

When running with `--dry-run`,`nflaunch`creates configuration files under `$TMPDIR/<WORKFLOWRUN_ID>/`:

- `job_config.json` - Complete job configuration
- `job_request.txt` - Batch API request that would be submitted

You can find the actual path in your log output:

```bash
[INFO] NextflowLauncher: Job config loaded from args: /var/folders/.../c537479f-.../job_config.json
[INFO] GCPBatchClient: [DRY-RUN] Will submit the following job request: /var/folders/.../c537479f-.../job_request.txt
```

Inspect these files to verify:
- All paths are correct
- Resources are properly configured
- Labels and metadata are as expected

### Submit the Job

Once validation passes, remove the `--dry-run` flag to submit:

```bash
nflaunch \
  --base-bucket BASE_BUCKET \
  --pipeline-name nf-core/demo \
  --pipeline-version 1.0.2 \
  --params-file examples/params.yaml \
  --samplesheet examples/samplesheet.csv \
  --config-file examples/resources.config \
  --project-id PROJECT_ID \
  --region REGION \
  --service-account-email SERVICE_ACCOUNT \
  --network NETWORK \
  --subnetwork SUBNETWORK \
  --labels '{"env": "test", "tool": "nflaunch"}'
```

## Run a Local (Non-Published) Pipeline

You can launch a pipeline from your local filesystem instead of a published registry.

### Using a Directory Path

Point `--pipeline-name` at the folder containing your pipeline:

```bash
nflaunch \
  --base-bucket BASE_BUCKET \
  --pipeline-name /Users/me/my-pipeline \
  --params-file /path/to/your/params.yaml \
  --project-id PROJECT_ID \
  --region REGION \
  --service-account-email SERVICE_ACCOUNT \
  --network NETWORK \
  --subnetwork SUBNETWORK \
  --labels '{"env":"test","tool":"nflaunch"}' \
  --dry-run
```

### Using Current Directory

If you run `nflaunch` from inside your pipeline directory, use `.` to indicate the current directory:

```bash
cd /path/to/my-pipeline
nflaunch \
  --base-bucket BASE_BUCKET \
  --pipeline-name . \
  --params-file params.yaml \
  --project-id PROJECT_ID \
  --region REGION \
  --service-account-email SERVICE_ACCOUNT \
  --network NETWORK \
  --subnetwork SUBNETWORK \
  --labels '{"env":"test","tool":"nflaunch"}'
```

## Understanding File Paths in Configuration Files

**Important:** The runner job reads files inside the container from `/etc/nextflow/` with the following structure:
- Generated configs: `/etc/nextflow/config/`
- Input files: `/etc/nextflow/input/`
- Logs: `/etc/nextflow/logs/`

Any file referenced inside `params.yaml` or a custom `.config` must use these paths to be accessible at runtime.

### Example: Samplesheet Path

When specifying a samplesheet path in `params.yaml`, use the container mount path:

```yaml
input: /etc/nextflow/input/samplesheet.csv
```

**NOT** the local path:

```yaml
input: examples/samplesheet.csv  # This won't work
```

### Example: nf-core/oncoanalyser params.yaml

```yaml
mode: wgts
genome: GRCh38_hmf
input: /etc/nextflow/input/samplesheet.csv
outdir: gs://my-bucket/results
processes_exclude: virusinterpreter,orange
```

## Monitoring Your Pipeline

After submission, `nflaunch` will output:

- **Job Name** - Name of the Batch job created
- **Workflowrun ID** - UUID for tracking this pipeline run
- **GCS Paths** - Locations of config files, logs, and outputs

### View Job Status

```bash
gcloud batch jobs describe JOB_NAME --location=REGION
```

### View Logs

```bash
gcloud batch jobs logs JOB_NAME --location=REGION
```

### Check Cloud Storage

Navigate to your base bucket to see the generated structure:

```bash
gsutil ls -r gs://BASE_BUCKET/run/
```

For detailed information about created resources, see [Cloud Resources](cloud-resources.md).

## Common Patterns

### Using Custom Nextflow Config

```bash
nflaunch \
  --pipeline-name nf-core/rnaseq \
  --config-file custom-resources.config \
  ...
```

### Specifying Pipeline Profile

```bash
nflaunch \
  --pipeline-name nf-core/sarek \
  --profile test \
  ...
```

### Using Spot Instances (Default)

Spot instances are enabled by default. To disable:

```bash
nflaunch \
  --pipeline-name ... \
  --no-spot \
  ...
```

## Next Steps

- **Review all CLI options** - See [CLI Reference](cli-reference.md)
- **Learn about plugins** - See [Plugins](plugins.md)
- **Understand cloud resources** - See [Cloud Resources](cloud-resources.md)
- **Explore examples** - Check the `examples/` directory in the repository

## Troubleshooting

### Permission Errors

If you encounter permission errors, verify your [GCP Setup](gcp-setup.md) is complete.

### File Not Found Errors (in nf-runner job)

Ensure file paths in your `params.yaml` use the `/etc/nextflow/input/` prefix for any file passed via `--samplesheet`.

### Network Errors

Check that Private Google Access is enabled on your subnetwork. See [GCP Setup - Network Configuration](gcp-setup.md#network-configuration).
