# Installation Guide

This guide covers installing `nflaunch` and setting up the required prerequisites.

## Prerequisites

Before installing nflaunch, ensure you have:

- **Python 3.10+**
- **[Google Cloud CLI](https://cloud.google.com/sdk/docs/install)** installed and initialized for your project

## Installation

### 1. Create a Virtual Environment (Recommended)

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install nflaunch from GitHub

```bash
pip install git+https://github.com/rodjc/nflaunch.git
```

### 3. Verify Installation

```bash
nflaunch --help
```

### 4. Make nflaunch Available on Your Shell PATH (Optional)

To use `nflaunch` without activating the environment each time, add the virtualenv's `bin` directory to your shell profile:

**For Bash users (`~/.bashrc` or `~/.bash_profile`):**
```bash
echo "export PATH=\"$(pwd)/.venv/bin:\$PATH\"" >> ~/.bashrc
source ~/.bashrc
```

**For Zsh users (`~/.zshrc`):**
```bash
echo "export PATH=\"$(pwd)/.venv/bin:\$PATH\"" >> ~/.zshrc
source ~/.zshrc
```

Adjust the path if you place the repository or virtual environment elsewhere.

## Next Steps

After installation, you'll need to:

1. **Configure GCP permissions** - See [GCP Setup Guide](gcp-setup.md)
2. **Try the quickstart** - Follow the [Quickstart Guide](quickstart.md)

## Troubleshooting

### Python Version Issues

If you encounter version conflicts, ensure you're using Python 3.10 or higher:

```bash
python3 --version
```

### Virtual Environment Issues

If `nflaunch` is not found after installation, ensure your virtual environment is activated:

```bash
source .venv/bin/activate
```

## Next Steps

Verify the Google Cloud CLI is properly installed:

```bash
gcloud --version
```

For installation issues, refer to the [official Google Cloud SDK documentation](https://cloud.google.com/sdk/docs/install).
