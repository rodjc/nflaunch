# Installation Guide

This guide covers installing `nflaunch` and setting up the required prerequisites.

## Prerequisites

Before installing nflaunch, ensure you have:

- **Python 3.10+**
- **[Google Cloud CLI](https://cloud.google.com/sdk/docs/install)** installed and initialized for your project

## Installation

### Step 1: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Step 2: Install nflaunch

**Option A: Install from PyPI (Recommended)**

```bash
pip install nflaunch
```


**Option B: Install from Source (Development)**

```bash
# Clone the repository
git clone https://github.com/rodjc/nflaunch.git
cd nflaunch

# Install in development mode
pip install -e ".[dev]"
```

### Step 3: Verify Installation

```bash
nflaunch --help
```

### Step 4: Add to PATH (Optional)

To use `nflaunch` without activating the virtual environment each time, add the virtualenv's `bin` directory to your shell profile:

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

**Note:** Adjust the path if you created the virtual environment in a different location.

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

For other installation issues, refer to the troubleshooting section above or open an issue on [GitHub](https://github.com/rodjc/nflaunch/issues).
