# Cloud Resources

This document describes the cloud resources created by`nflaunch`when you submit a pipeline job.

## Overview

When you run `nflaunch`, it creates resources in two main locations:

1. **Google Batch** - A runner job that orchestrates the Nextflow pipeline
2. **Google Cloud Storage** - A structured directory hierarchy for configs, work files, and outputs

## Google Batch Job

### Job Naming

A **runner** job will be created with the following naming pattern:

```
nf-runner-<SAMPLE_ID>-<WORKFLOWRUN_ID_PREFIX>
```

### Example

```
nf-runner-tumor123-da0b69db
```

Where:
- `tumor123` - Derived from `--sample-id TUMOR123` (lowercased; if omitted, an 8-character random ID is generated)
- `da0b69db` - First 8 characters of the workflowrun ID UUID

You can use this value to:
- Locate the job in the Batch console
- Find associated config files and logs in Cloud Storage
- Track the job via `gcloud batch jobs describe`

### Job Properties

The Batch job includes:

- **Container**: Nextflow Docker image (configurable via `--container-image`)
- **Service Account**: Specified via `--service-account-email`
- **Network**: VPC network and subnetwork
- **Labels**: Custom labels from `--labels`
- **Resources**: CPU, memory, and machine type configurations
- **Volumes**: Mounted directories for configs and work files

## Google Cloud Storage Structure

### Base Structure

The following structure is created under the base bucket specified via `--base-bucket`.

**Example Input:**
- `--base-bucket` `gs://my-nextflow-bucket`
- `--sample-id` `TUMOR123`

**Generated Values:**
- Job name: `nf-runner-tumor123-da0b69db`
- Workflowrun ID: `da0b69db-fb80-4474-a46d-61ef7a118617`

### Directory Layout

```
my-nextflow-bucket/
├── cache/                                          # Nextflow cache for resuming pipelines
│   └── [Nextflow cache files]                      # Auto-managed by Nextflow
│
├── work/                                           # Nextflow work directory
│   └── [Intermediate process files]                # Auto-managed by Nextflow
│
└── run/                                            # Pipeline run metadata and configs
    └── da0b69db-fb80-4474-a46d-61ef7a118617/       # Workflowrun ID (UUID)
        ├── config/                                 # Configuration files
        │   ├── custom.config                       # From --config-file
        │   ├── gcp.config                          # Auto-generated GCP config
        │   └── [pipeline files]                    # Local pipeline .nf files/directories
        │
        ├── input/                                  # Input files
        │   ├── params.yaml                         # From --params-file
        │   └── samplesheet.csv                     # From --samplesheet
        │
        └── logs/                                   # Execution logs and reports
            ├── nextflow.log                        # Main Nextflow execution log
            ├── timeline_20250805_134200.html       # Timeline visualization
            ├── trace_20250805_134200.txt           # Execution trace
            ├── report_20250805_134200.html         # Execution report
            └── dag_20250805_134200.html            # DAG visualization
```

### Path Configuration

These paths can be customized via CLI options:

| Directory | Default Path | CLI Option |
|-----------|--------------|------------|
| Cache | `gs://<BASE_BUCKET>/cache` | `--remote-cache-path` |
| Work | `gs://<BASE_BUCKET>/work` | N/A (Nextflow default) |
| Run | `gs://<BASE_BUCKET>/run` | `--remote-run-path` |

### Cache Directory

**Path**: `gs://<BASE_BUCKET>/cache` (default)

The cache directory stores Nextflow's task cache, enabling:
- **Resume functionality** - Restart failed pipelines without re-running successful tasks
- **Incremental runs** - Only execute changed tasks when parameters are updated

**Important**: This directory should be persistent across pipeline runs.

### Work Directory

**Path**: `gs://<BASE_BUCKET>/work` (default)

The work directory contains:
- Intermediate files from each process
- Staged input files
- Process execution scripts
- Task logs and exit codes

**Note**: This directory can grow large. Consider implementing a cleanup policy for old runs.

### Run Directory

**Path**: `gs://<BASE_BUCKET>/run/<WORKFLOWRUN_ID>` (default)

#### config/ Subdirectory

Stores generated configuration files:

- **`custom.config`** - Custom Nextflow configuration (from `--config-file`)
- **`gcp.config`** - Auto-generated GCP-specific configuration
- Local pipeline files (if `.nf` file or directory is provided)

#### input/ Subdirectory

Stores user input files:

- **`params.yaml`** - Pipeline parameters (from `--params-file`)
- **`samplesheet.csv`** - Input samplesheet (from `--samplesheet`)

#### logs/ Subdirectory

Stores Nextflow execution logs and reports:

- **`nextflow.log`** - Main Nextflow execution log
- **`timeline_*.html`** - Timeline of task execution
- **`trace_*.txt`** - Detailed trace of all tasks
- **`report_*.html`** - Summary execution report
- **`dag_*.html`** - Directed acyclic graph visualization

These files are generated automatically by Nextflow during and after pipeline execution.

**Container Mount**: The workflow run directory is mounted at `/etc/nextflow/` inside the runner container, with subdirectories at `/etc/nextflow/config/`, `/etc/nextflow/input/`, and `/etc/nextflow/logs/`.

## Pipeline Output Directory

Pipeline outputs are stored in the location specified by the `outdir` parameter in your `params.yaml`:

```yaml
outdir: gs://my-bucket/results
```

This is **separate** from the run directory and typically contains your final analysis results.

## Resource Lifecycle

### Temporary Resources

- **Batch Job**: Removed automatically after completion (configurable retention)
- **Local temp files**: Stored in `$TMPDIR/<WORKFLOWRUN_ID>/` on your machine during submission

### Persistent Resources

- **Cache directory**: Should be retained for resume functionality
- **Work directory**: Can be cleaned up after successful runs
- **Run directory**: Contains valuable metadata and configs; recommended to retain
- **Output directory**: Your final results; should be retained

## Cleanup Recommendations

### After Successful Runs

```bash
# Remove work directory for a specific run (after verifying outputs)
gsutil -m rm -r gs://my-bucket/work/

# Or use Nextflow's cleanup
nextflow clean -f
```

### Automated Cleanup

Consider setting up lifecycle policies on your bucket:

```bash
# Example: Delete work/ files older than 30 days
gsutil lifecycle set lifecycle.json gs://my-bucket
```

**lifecycle.json**:
```json
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {
          "age": 30,
          "matchesPrefix": ["work/"]
        }
      }
    ]
  }
}
```

## Monitoring Resources

### View Batch Jobs

```bash
gcloud batch jobs list --location=REGION
gcloud batch jobs describe JOB_NAME --location=REGION
```

### View Storage Usage

```bash
# List all runs
gsutil ls gs://my-bucket/run/

# Check size of specific run
gsutil du -sh gs://my-bucket/run/da0b69db-fb80-4474-a46d-61ef7a118617/

# View work directory size
gsutil du -sh gs://my-bucket/work/
```

### Access Logs

```bash
# View Batch job logs
gcloud batch jobs logs JOB_NAME --location=REGION

# View Nextflow logs in Cloud Storage
gsutil cat gs://my-bucket/run/<WORKFLOWRUN_ID>/meta/.nextflow.log
```

## See Also

- [Quickstart Guide](quickstart.md) - Running your first pipeline
- [CLI Reference](cli-reference.md) - All command-line options
- [GCP Setup](gcp-setup.md) - Required permissions and setup
