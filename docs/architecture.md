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
class Backend(ABC):
    @abstractmethod
    def submit_job(self, job_config: JobConfig) -> str:
        """Submit job to the backend."""
        pass
```

**Plugin Interface** (`plugins/base.py`):
```python
class Plugin(ABC):
    @abstractmethod
    def run(self, job_config: JobConfig) -> JobConfig:
        """Execute plugin logic and modify job config."""
        pass
```

**Command Interface** (`command/base.py`):
```python
class Command(ABC):
    @abstractmethod
    def build(self) -> str:
        """Build the command string."""
        pass
```

### 2. Registry Pattern

Backends and plugins are registered dynamically using a registry pattern:

```python
# utils/registry.py
class Registry:
    def register(self, name: str, cls: type) -> None:
        self._registry[name] = cls

    def get(self, name: str) -> type:
        return self._registry[name]

backend_registry = Registry()
plugin_registry = Registry()
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

## Extension Points

### Adding a New Backend

1. Create a new directory under `backends/` (e.g., `backends/aws/`)
2. Implement the `Backend` abstract class
3. Register in `utils/registry.py`:
   ```python
   backend_registry.register("aws-batch", AWSBatchBackend)
   ```
4. Add backend-specific CLI arguments in `cli/parser.py`

### Adding a New Plugin

1. Create a new directory under `plugins/` (e.g., `plugins/myplugin/`)
2. Implement the `Plugin` abstract class
3. Register in `plugins/__init__.py`:
   ```python
   plugin_registry.register("myplugin", MyPlugin)
   ```
4. Add plugin README with documentation

### Adding a New Workflow Type

1. Create a new command class in `command/` implementing `Command`
2. Add workflow-specific logic in a new launcher
3. Update CLI to support the new workflow type

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

### Environment Variables

- `NF_LAUNCH_TMPDIR` - Custom temporary directory
- `TMPDIR` - Fallback temporary directory
- `NF_LAUNCH_LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)

### Configuration Files

- **User-provided**:
  - `params.yaml` - Pipeline parameters
  - `*.config` - Custom Nextflow configs
  - `samplesheet.csv` - Input data

- **Auto-generated**:
  - `gcp.config` - GCP-specific Nextflow config
  - `job_config.json` - Complete job configuration (dry-run)
  - `job_request.txt` - Batch API request (dry-run)

## Testing Strategy

While tests are currently not implemented (see improvement suggestions), the architecture supports:

- **Unit tests** - For validators, utilities, command builders
- **Integration tests** - For backend operations (with mocked APIs)
- **End-to-end tests** - Using `--dry-run` mode

## See Also

- [Installation Guide](installation.md) - Setting up the development environment
- [Plugins](plugins.md) - Plugin development guide
- [CLI Reference](cli-reference.md) - All command-line options
- [CHANGELOG](../CHANGELOG.md) - Version history and changes
