# Architecture

This document describes the`nflaunch`repository structure and design patterns.

## Repository Layout

```
.
├── nflaunch/              # Python package sources
│   ├── __init__.py
│   ├── __main__.py        # Entry point for `python -m nflaunch`
│   ├── backends/          # Cloud backend implementations
│   │   ├── base.py        # Abstract backend interface
│   │   └── gcp/           # Google Cloud Platform backend
│   │       ├── batch.py   # GCP Batch client
│   │       ├── file.py    # GCS file operations
│   │       ├── job.py     # Job configuration builders
│   │       └── templates/ # GCP config templates
│   ├── cli/               # Command-line interface
│   │   ├── formatter.py   # Help text formatting
│   │   ├── main.py        # Main entry point
│   │   ├── parser.py      # Argument parsing
│   │   └── validator.py   # Input validation
│   ├── command/           # Workflow command builders
│   │   ├── base.py        # Abstract command interface
│   │   └── nextflow.py    # Nextflow-specific commands
│   ├── launcher/          # Orchestration layer
│   │   └── nextflow.py    # Nextflow launcher logic
│   ├── plugins/           # Plugin system
│   │   ├── __init__.py    # Plugin registration
│   │   ├── base.py        # Abstract plugin interface
│   │   └── oncoanalyser/  # Example plugin
│   └── utils/             # Shared utilities
│       ├── logger.py      # Logging configuration
│       ├── paths.py       # Path manipulation
│       ├── registry.py    # Backend/plugin registry
│       ├── templates.py   # Template rendering
│       └── upload.py      # File upload helpers
├── docs/                  # Documentation
│   ├── README.md          # Documentation index
│   ├── installation.md    # Installation guide
│   ├── gcp-setup.md       # GCP configuration
│   ├── quickstart.md      # Getting started guide
│   ├── cli-reference.md   # CLI options reference
│   ├── cloud-resources.md # Cloud resource details
│   ├── plugins.md         # Plugin system guide
│   └── architecture.md    # This file
├── examples/              # Sample configuration files
│   ├── params.yaml        # Example pipeline parameters
│   ├── resources.config   # Example resource config
│   ├── run_demo.sh        # Helper script
│   └── samplesheet.csv    # Example samplesheet
├── tests/                 # Unit tests
│   ├── test_dependencies.py
│   └── test_gcs_structure.py
├── pyproject.toml         # Build and tooling configuration
├── requirements.txt       # Python dependencies
├── CHANGELOG.md           # Version history
├── LICENSE                # Apache 2.0 license
└── README.md              # Project overview
```

## Design Patterns

### 1. Abstract Base Classes

nflaunch uses abstract base classes to define interfaces for extensibility:

**Backend Interface** (`backends/base.py`):
```python
class BatchClient(ABC):
    @abstractmethod
    def stage_resources(self) -> None:
        """Stage input files and configuration artifacts to cloud storage."""
        pass

    @abstractmethod
    def launch_job(self) -> None:
        """Submit the job to the target cloud batch system."""
        pass

    @abstractmethod
    def cancel_job(self) -> None:
        """Terminate an active cloud batch job."""
        pass
```

**Plugin Interface** (`plugins/base.py`):
```python
class Plugin(ABC):
    def __init__(self, job_config: JobConfig) -> None:
        """Initialize the plugin with the active job configuration."""
        pass

    @abstractmethod
    def load(self) -> None:
        """Load and apply plugin-specific configuration data."""
        pass
```

**Command Interface** (`command/base.py`):
```python
class CommandBuilder(ABC):
    def __init__(self, job_config: JobConfig) -> None:
        """Initialize the command builder with the active job configuration."""
        pass

    @abstractmethod
    def build(self) -> str:
        """Construct the complete command-line string needed to run the workflow."""
        pass
```

### 2. Registry Pattern

Backends and plugins are registered dynamically using a registry pattern:

```python
# utils/registry.py
class BackendRegistry:
    def register(self, key: str, batch_client_cls: type[BatchClient],
                 job_config_builder_cls: type[JobConfigBuilder]) -> None:
        self._registry[key] = (batch_client_cls, job_config_builder_cls)

    def get(self, key: str) -> tuple[type[BatchClient], type[JobConfigBuilder]]:
        return self._registry[key]

class PluginRegistry:
    def register(self, key: str, cls: type[Plugin]) -> None:
        self._registry[key] = cls

    def get(self, key: str) -> type[Plugin]:
        return self._registry[key]

backend_registry = BackendRegistry()
plugin_registry = PluginRegistry()
```

This allows easy addition of new backends and plugins without modifying core code.

### 3. Builder Pattern

Job configurations are built using the builder pattern:

```python
# backends/gcp/job.py
class JobConfigBuilder:
    @classmethod
    def build(cls, args: Namespace) -> JobConfig:
        # Build job configuration from arguments
        return JobConfig(...)
```

### 4. Template Pattern

Configuration files are generated from templates:

```python
# utils/templates.py
def render_template(template_path: str, context: dict) -> str:
    with open(template_path) as f:
        template = Template(f.read())
    return template.substitute(context)
```

## Component Responsibilities

### CLI Layer (`cli/`)

**Purpose**: User interface for the tool

- **`main.py`** - Entry point, orchestrates the flow
- **`parser.py`** - Defines all CLI arguments and options
- **`validator.py`** - Custom argument type validators (email, JSON, positive int, etc.)
- **`formatter.py`** - Custom help text formatting

### Backend Layer (`backends/`)

**Purpose**: Cloud platform abstraction

- **`base.py`** - Defines the backend interface
- **`gcp/batch.py`** - GCP Batch API client implementation
- **`gcp/file.py`** - GCS file upload operations
- **`gcp/job.py`** - GCP-specific job configuration builders
- **`gcp/templates/`** - Nextflow config templates for GCP

### Command Layer (`command/`)

**Purpose**: Workflow command generation

- **`base.py`** - Defines command interface
- **`nextflow.py`** - Builds Nextflow CLI commands with appropriate flags

### Launcher Layer (`launcher/`)

**Purpose**: Orchestration of the entire job submission process

- **`nextflow.py`** - Coordinates backend, plugins, and command building

### Plugin Layer (`plugins/`)

**Purpose**: Pipeline-specific customization

- **`base.py`** - Defines plugin interface
- **`__init__.py`** - Plugin registration
- **Individual plugins** - Self-contained plugin implementations

### Utilities (`utils/`)

**Purpose**: Shared helper functions

- **`logger.py`** - Centralized logging configuration
- **`paths.py`** - Path resolution and manipulation
- **`registry.py`** - Backend and plugin registration
- **`templates.py`** - Template rendering helpers
- **`upload.py`** - Parallel file upload utilities

## Data Flow

### Job Submission Flow

```
1. CLI Input (cli/parser.py)
   ↓
2. Validation (cli/validator.py)
   ↓
3. Backend Selection (utils/registry.py)
   ↓
4. Job Config Building (backends/gcp/job.py)
   ↓
5. Plugin Execution (plugins/*)
   ↓
6. Command Building (command/nextflow.py)
   ↓
7. File Upload (backends/gcp/file.py)
   ↓
8. Job Submission (backends/gcp/batch.py)
```

### Configuration Flow

```
User Args → JobConfig → Plugin Modification → Template Rendering → Cloud Submission
```

## Type System

nflaunch uses Python type hints extensively:

- **Function signatures** - All functions have type-annotated parameters and return types
- **Dataclasses** - Immutable configuration objects using `@dataclass(frozen=True)`
- **Type checking** - Configured with mypy in `pyproject.toml`

Example:
```python
from dataclasses import dataclass

@dataclass(frozen=True)
class JobConfig:
    project_id: str
    region: str
    service_account: str
    network: str
    subnetwork: str
```

## Error Handling

nflaunch uses Python's exception system with custom error types where appropriate:

- **Validation errors** - `argparse.ArgumentTypeError` for CLI validation
- **File errors** - Standard `FileNotFoundError`, `IOError`
- **API errors** - Google API exceptions for GCP operations
- **Logging** - All errors are logged before raising

## Configuration Management

### Configuration Files

- **User-provided**:
  - `params.yaml` - Pipeline parameters
  - `*.config` - Custom Nextflow configs
  - `samplesheet.csv` - Input data

- **Auto-generated**:
  - `gcp.config` - GCP-specific Nextflow config
  - `job_config.json` - Complete job configuration (dry-run)
  - `job_request.txt` - Batch API request (dry-run)

## See Also

- [Installation Guide](installation.md) - Setting up the development environment
- [Plugins](plugins.md) - Plugin development guide
- [CLI Reference](cli-reference.md) - All command-line options
- [CHANGELOG](../CHANGELOG.md) - Version history and changes
