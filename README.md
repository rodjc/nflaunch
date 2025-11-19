# nflaunch

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-green.svg)](https://opensource.org/licenses/Apache-2.0)

`nflaunch` is a command-line tool designed to simplify the launching of **Nextflow pipelines** on cloud batch services.
It abstracts complex cloud configurations into a unified interface, currently supporting **Google Cloud Batch**.

*This tool is under active development and intended for users with experience managing cloud resources and Nextflow pipelines.
Ensure you understand the configurations and implications of job submissions before using it in production environments.*

---

## Table of Contents

- [Key Features](#key-features)
- [Quick Start](#quick-start)
- [Documentation](#documentation)
- [Usage Example](#usage-example)
- [Contributing](#contributing)
- [License](#license)

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
python3 -m venv .venv
source .venv/bin/activate
pip install git+https://github.com/rodjc/nflaunch.git
```

**Verify installation:**
```bash
nflaunch --help
```

For detailed installation instructions, see the [Installation Guide](docs/installation.md).

### GCP Setup

Configure required permissions and authentication:

```bash
# Authenticate
gcloud auth login
gcloud auth application-default login
```

Enable the following APIs in your GCP project:
- Google Cloud Batch API (`batch.googleapis.com`)
- Google Cloud Storage API (`storage.googleapis.com`)

For complete GCP setup instructions, see the [GCP Setup Guide](docs/gcp-setup.md).

## Documentation

Comprehensive documentation is available in the [`docs/`](docs/) directory:

### Getting Started
- **[Installation Guide](docs/installation.md)** - Detailed installation instructions and setup
- **[Quickstart Guide](docs/quickstart.md)** - Step-by-step examples to run your first pipeline
- **[GCP Setup](docs/gcp-setup.md)** - Google Cloud permissions, authentication, and configuration

### Reference
- **[CLI Reference](docs/cli-reference.md)** - Complete command-line options and examples
- **[Cloud Resources](docs/cloud-resources.md)** - Understanding resources created in GCP
- **[Plugins](docs/plugins.md)** - Plugin system overview and development guide
- **[Architecture](docs/architecture.md)** - Repository structure and design patterns

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
  --region us-central1 \
  --service-account-email sa@my-project.iam.gserviceaccount.com \
  --network default \
  --subnetwork default \
  --labels '{"env": "test", "tool": "nflaunch"}' \
  --dry-run
```

Remove `--dry-run` to submit the job.

For more examples and detailed usage instructions, see the [Quickstart Guide](docs/quickstart.md).

## License

This project is distributed under the terms of the [Apache License 2.0](LICENSE).

---

**Documentation**: [docs/](docs/) | **Examples**: [examples/](examples/) | **Changelog**: [CHANGELOG.md](CHANGELOG.md)
