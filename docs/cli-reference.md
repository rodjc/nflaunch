# CLI Reference

Complete reference for all `nflaunch` command-line options.

## General Options

### Required

| Flag                          | Type         | Description                                                                                                         |
| ----------------------------- | ------------ | ------------------------------------------------------------------------------------------------------------------- |
| `--base-bucket`               | string       | Bucket for configs, logs, cache, and work dirs. Accepts `my-bucket` or `gs://my-bucket`. Internally normalized to a bucket name (no `gs://`). |

### Optional

| Flag                          | Type         | Description                                                                                                         |
| ----------------------------- | ------------ | ------------------------------------------------------------------------------------------------------------------- |
| `--help`                      | flag         | Show help message and exit.                                                                                         |
| `--version`                   | flag         | Show program version and exit (from installed package metadata).                                                    |
| `--container-image`           | string       | Docker image with Nextflow and deps. If no tag is provided,`nflaunch`appends `:<nextflow_version>`. Default: `nextflow/nextflow`. |
| `--sample-id`                 | string       | Identifier for the input sample(s).                                                                                 |
| `--dry-run`                   | flag         | Print job configuration without submitting to the backend.                                                          |
| `--backend`                   | string       | Batch backend to use. Default: `google-batch`. Accepts `google-batch` or alias `gcp-batch`.                         |
| `--remote-cache-path`         | string       | Remote cache location. If not a full `gs://…` URI (or empty), defaults post-parse to `<BASE_BUCKET>/cache`.         |
| `--remote-run-path`           | string       | Where config & reports (report/trace/timeline) are stored. If a folder name is given (e.g. `run`), becomes `<BASE_BUCKET>/<folder>`. Default: `<BASE_BUCKET>/run`. |

## GCP Batch Options

### Required

| Flag                          | Type         | Description                                                                                                         |
| ----------------------------- | ------------ | ------------------------------------------------------------------------------------------------------------------- |
| `--project-id`                | string       | Google Cloud project ID.                                                                                            |
| `--region`                    | string       | Google Cloud region in which to run the Batch job.                                                                  |
| `--service-account-email`     | string       | Runner job service account.                                                                                         |
| `--network`                   | string       | VPC network name where the jobs will run.                                                                           |
| `--subnetwork`                | string       | Subnetwork name where the jobs will run.                                                                            |

### Optional

| Flag                          | Type         | Description                                                                                                         |
| ----------------------------- | ------------ | ------------------------------------------------------------------------------------------------------------------- |
| `--spot` / `--no-spot`        | flag         | Use Spot instances (`--no-spot` to disable). Default: enabled.                                                      |
| `--labels`                    | JSON object  | Labels for the Nextflow runner (validated as JSON object). Default: `{}`.                                           |
| `--upload-max-workers`        | int          | Max parallel workers for uploads. Default: `0`, which means auto (CPU count).                                       |
| `--machine-type`              | string       | GCP machine type for Batch workers (e.g., `e2-standard-4`). Default: `e2-small`.                                    |
| `--cpu-milli`                 | int          | CPU request per task in millicores (e.g., `4000` for 4 vCPU). Default: `2000`.                                      |
| `--memory-mib`                | int          | Memory request per task in MiB. Default: `2000`.                                                                    |

**Note:**`nflaunch`always requests instances **without public IP addresses**. Public networking is not currently supported.

## Nextflow Pipeline Options

### Required

| Flag                          | Type         | Description                                                                                                         |
| ----------------------------- | ------------ | ------------------------------------------------------------------------------------------------------------------- |
| `--pipeline-name`             | string       | `nf-core/<pipeline>`, a local folder path (e.g. `/path/to/pipeline`), or `.` for the current directory.            |

### Optional

| Flag                          | Type         | Description                                                                                                         |
| ----------------------------- | ------------ | ------------------------------------------------------------------------------------------------------------------- |
| `--nextflow-version`          | string       | Version of Nextflow to use. Default: `25.04.6`.                                                                     |
| `--pipeline-version`          | string       | Specific pipeline version/tag.                                                                                      |
| `--profile`                   | string       | Profile defined in the Nextflow config.                                                                             |
| `--params-file`               | path         | YAML/JSON file with pipeline parameters.                                                                            |
| `--config-file`               | path         | Custom Nextflow config file.                                                                                        |
| `--executor-config-file`      | path         | Nextflow cloud executor config file.                                                                                |
| `--samplesheet`               | path         | CSV samplesheet used by some pipelines.                                                                             |
| `--resume`                    | string       | Resume a previous run. Format: `WORKFLOWRUN_ID,WORKFLOW_SESSION`.                                                   |

## Plugin Options

### Optional

| Flag                          | Type         | Description                                                                                                         |
| ----------------------------- | ------------ | ------------------------------------------------------------------------------------------------------------------- |
| `--plugin`                    | string       | Plugin name to add backend-specific behavior.                                                                       |
| `--plugin-options`            | JSON object  | JSON object of plugin options (e.g., `'{"sample_group": "clinical"}'`). Validated to be a JSON object. Default: `{}`. |

## Usage Examples

### Basic Pipeline Run

```bash
nflaunch \
  --base-bucket my-bucket \
  --pipeline-name nf-core/rnaseq \
  --pipeline-version 3.14.0 \
  --params-file params.yaml \
  --project-id my-project \
  --region us-central1 \
  --service-account-email sa@my-project.iam.gserviceaccount.com \
  --network default \
  --subnetwork default
```

### Dry Run Validation

```bash
nflaunch \
  --base-bucket my-bucket \
  --pipeline-name nf-core/sarek \
  --params-file params.yaml \
  --project-id my-project \
  --region us-central1 \
  --service-account-email sa@my-project.iam.gserviceaccount.com \
  --network default \
  --subnetwork default \
  --dry-run
```

### Local Pipeline with Custom Resources

```bash
nflaunch \
  --base-bucket my-bucket \
  --pipeline-name /path/to/pipeline \
  --config-file resources.config \
  --machine-type e2-standard-4 \
  --cpu-milli 4000 \
  --memory-mib 16000 \
  --project-id my-project \
  --region us-central1 \
  --service-account-email sa@my-project.iam.gserviceaccount.com \
  --network default \
  --subnetwork default
```

### Using Plugins

```bash
nflaunch \
  --base-bucket my-bucket \
  --pipeline-name nf-core/oncoanalyser \
  --params-file params.yaml \
  --plugin oncoanalyser \
  --plugin-options '{"remote_sample_bucket_uri": "gs://samples", "filetype": "bam"}' \
  --sample-id TUMOR123,NORMAL456 \
  --project-id my-project \
  --region us-central1 \
  --service-account-email sa@my-project.iam.gserviceaccount.com \
  --network default \
  --subnetwork default
```

### Resuming a Previous Run

```bash
nflaunch \
  --base-bucket my-bucket \
  --pipeline-name nf-core/rnaseq \
  --resume da0b69db-fb80-4474-a46d-61ef7a118617,a1b2c3d4-e5f6-7890 \
  --project-id my-project \
  --region us-central1 \
  --service-account-email sa@my-project.iam.gserviceaccount.com \
  --network default \
  --subnetwork default
```

### Disable Spot Instances

```bash
nflaunch \
  --base-bucket my-bucket \
  --pipeline-name nf-core/chipseq \
  --params-file params.yaml \
  --no-spot \
  --project-id my-project \
  --region us-central1 \
  --service-account-email sa@my-project.iam.gserviceaccount.com \
  --network default \
  --subnetwork default
```

### Custom Labels

```bash
nflaunch \
  --base-bucket my-bucket \
  --pipeline-name nf-core/atacseq \
  --params-file params.yaml \
  --labels '{"project": "research", "team": "bioinformatics", "cost-center": "lab-a"}' \
  --project-id my-project \
  --region us-central1 \
  --service-account-email sa@my-project.iam.gserviceaccount.com \
  --network default \
  --subnetwork default
```

## See Also

- [Quickstart Guide](quickstart.md) - Step-by-step examples
- [Plugins](plugins.md) - Plugin system documentation
- [GCP Setup](gcp-setup.md) - GCP configuration and permissions
- [Cloud Resources](cloud-resources.md) - Understanding created resources
