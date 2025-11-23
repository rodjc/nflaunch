# nflaunch

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://img.shields.io/pypi/v/nflaunch.svg)](https://pypi.org/project/nflaunch/)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-green.svg)](https://opensource.org/licenses/Apache-2.0)

`nflaunch` is a command-line tool designed to simplify the launching of **Nextflow pipelines** on cloud batch services.
It abstracts complex cloud configurations into a unified interface, currently supporting **Google Cloud Batch**.

*This tool is under active development and intended for users with experience managing cloud resources and Nextflow pipelines.
Ensure you understand the configurations and implications of job submissions before using it in production environments.*

---

## Table of Contents

- [Key Features](https://github.com/rodjc/nflaunch/tree/main?tab=readme-ov-file#key-features)
- [Quick Start](https://github.com/rodjc/nflaunch/tree/main?tab=readme-ov-file#quick-start)
- [Documentation](https://github.com/rodjc/nflaunch/tree/main?tab=readme-ov-file#documentation)
- [Usage Example](https://github.com/rodjc/nflaunch/tree/main?tab=readme-ov-file#usage-example)
- [License](https://github.com/rodjc/nflaunch/tree/main?tab=readme-ov-file#license)

---

## Key Features

- **GCP Batch Support** - Automated volume mounting and job execution on Google Cloud
- **Dry-Run Mode** - Validate job configurations before submission
- **Plugin System** - Extensible architecture for pipeline-specific enhancements
- **Local & Remote Pipelines** - Support for both published (e.g. nf-core public pipelines) and local pipeline directories
- **Resume Capability** - Resume failed pipeline runs

## Quick Start

### Prerequisites

- Python 3.10+
- [Google Cloud CLI](https://cloud.google.com/sdk/docs/install) installed and authenticated

### Installation

```bash
pip install nflaunch
```

**Verify installation:**
```bash
nflaunch --help
```

For detailed installation instructions, see the [Installation Guide](https://github.com/rodjc/nflaunch/blob/main/docs/installation.md).

### GCP Setup

Configure required permissions and authentication:

```bash
gcloud auth login
gcloud auth application-default login
```

Enable the following APIs in your GCP project:
- Google Cloud Batch API (`batch.googleapis.com`)
- Google Cloud Storage API (`storage.googleapis.com`)

For complete GCP setup instructions, see the [GCP Setup Guide](https://github.com/rodjc/nflaunch/blob/main/docs/gcp-setup.md).

## Documentation

Comprehensive documentation is available in the [`docs/`](https://github.com/rodjc/nflaunch/tree/main/docs/) directory:

### Getting Started
- **[Installation Guide](https://github.com/rodjc/nflaunch/blob/main/docs/installation.md)** - Detailed installation instructions and setup
- **[Quickstart Guide](https://github.com/rodjc/nflaunch/blob/main/docs/quickstart.md)** - Step-by-step examples to run your first pipeline
- **[GCP Setup](https://github.com/rodjc/nflaunch/blob/main/docs/gcp-setup.md)** - Google Cloud permissions, authentication, and configuration

### Reference
- **[CLI Reference](https://github.com/rodjc/nflaunch/blob/main/docs/cli-reference.md)** - Complete command-line options and examples
- **[Cloud Resources](https://github.com/rodjc/nflaunch/blob/main/docs/cloud-resources.md)** - Understanding resources created in GCP
- **[Plugins](https://github.com/rodjc/nflaunch/blob/main/docs/plugins.md)** - Plugin system overview and development guide

## Usage Example

Run the nf-core/demo pipeline with dry-run validation:

```bash
nflaunch \
  --base-bucket my-nextflow-bucket \
  --pipeline-name nf-core/demo \
  --pipeline-version 1.0.2 \
  --params-file examples/params.yaml \
  --samplesheet examples/samplesheet.csv \
  --config-file examples/resources.config \
  --project-id my-gcp-project \
  --region europe-west4 \
  --service-account-email sa@my-project.iam.gserviceaccount.com \
  --network default \
  --subnetwork default \
  --labels '{"env": "test", "tool": "nflaunch"}' \
  --dry-run
```

Remove `--dry-run` to submit the job.

For more examples and detailed usage instructions, see the [Quickstart Guide](https://github.com/rodjc/nflaunch/blob/main/docs/quickstart.md).

## License

This project is distributed under the terms of the [Apache License 2.0](https://github.com/rodjc/nflaunch/blob/main/LICENSE).

---

**Documentation**: [docs/](https://github.com/rodjc/nflaunch/tree/main/docs/) | **Examples**: [examples/](https://github.com/rodjc/nflaunch/tree/main/examples/) | **Changelog**: [CHANGELOG.md](https://github.com/rodjc/nflaunch/blob/main/CHANGELOG.md)
