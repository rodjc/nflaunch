# nflaunch

`nflaunch` is a command-line tool designed to simplify the launching of **Nextflow pipelines** on cloud batch services.
It abstracts complex cloud configurations into a unified interface, currently supporting **Google Cloud Batch**.

*This tool is under active development and intended for users with experience managing cloud resources and Nextflow pipelines.
Ensure you understand the configurations and implications of job submissions before using it in production environments.*

## Quick Start

### Prerequisites

- Python 3.10+
- [Google Cloud CLI](https://cloud.google.com/sdk/docs/install) installed and authenticated

### Installation

```bash
git clone https://github.com/rodjc/nflaunch.git
cd nflaunch
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

**Verify installation:**
```bash
nflaunch --help
```

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
