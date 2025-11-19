# Plugins

nflaunch includes a plugin system to extend and customize pipeline behavior for specific workflows.

## Overview

Plugins enable pipeline-specific enhancements such as:

- Auto-generating samplesheets from metadata
- Preprocessing input files
- Validating pipeline-specific requirements
- Adding custom configuration logic

All available plugins are located in the repository under:

```
nflaunch/plugins/
```

## Using Plugins

To use a plugin, specify it via the command line:

```bash
nflaunch \
  --plugin PLUGIN_NAME \
  --plugin-options JSON_OPTIONS \
  ...
```

### Plugin Options

Plugin options are passed as a JSON object:

```bash
--plugin-options '{"key": "value", "another_key": 123}'
```

The available options depend on the specific plugin being used. Refer to each plugin's documentation for details.

## Available Plugins

### oncoanalyser

**Purpose**: Generate samplesheets for the [nf-core/oncoanalyser](https://nf-co.re/oncoanalyser) pipeline from paired tumor-normal sample identifiers.

**Documentation**: See [`nflaunch/plugins/oncoanalyser/README.md`](../nflaunch/plugins/oncoanalyser/README.md)

**Quick Example**:

```bash
nflaunch \
  --pipeline-name nf-core/oncoanalyser \
  --pipeline-version 2.2.0 \
  --plugin oncoanalyser \
  --plugin-options '{"remote_sample_bucket_uri": "gs://my-bucket/samples", "filetype": "bam"}' \
  --sample-id TUMOR123,NORMAL456 \
  --params-file params.yaml \
  --project-id my-project \
  --region us-central1 \
  --service-account-email sa@my-project.iam.gserviceaccount.com \
  --network default \
  --subnetwork default
```

**Required Plugin Options**:
- `remote_sample_bucket_uri` - GCS URI where sample files are located
- `filetype` - File extension (`bam` or `cram`)

**Required CLI Options**:
- `--sample-id` - Comma-separated tumor and normal IDs (e.g., `TUMOR123,NORMAL456`)

For complete documentation, see the [oncoanalyser plugin README](../nflaunch/plugins/oncoanalyser/README.md).

## Plugin Architecture

### How Plugins Work

Plugins implement the `Plugin` base class and can:

1. **Modify job configuration** - Add or modify parameters before job submission
2. **Generate files** - Create samplesheets, configs, or other required files
3. **Validate inputs** - Check for required options and file existence
4. **Interact with cloud storage** - Upload/download files from GCS

### Plugin Lifecycle

1. **Registration** - Plugin is registered in the plugin registry
2. **Initialization** - Plugin receives job configuration containing CLI arguments and plugin options
3. **Execution** - Plugin's `load()` method is called before job submission
4. **Configuration** - Plugin modifies the job config attributes as needed

### Plugin Interface

All plugins must implement:

```python
from nflaunch.plugins.base import Plugin
from nflaunch.backends.base import JobConfig

class MyPlugin(Plugin):
    def __init__(self, job_config: JobConfig) -> None:
        super().__init__(job_config)
        # Additional initialization if needed

    def load(self) -> None:
        # Plugin logic here
        # Access job config via self.job_config
        # Modify job_config attributes as needed
```

## Developing Custom Plugins

### Plugin Structure

To create a new plugin:

1. Create a new directory under `nflaunch/plugins/`:
   ```
   nflaunch/plugins/my_plugin/
   ├── __init__.py
   ├── my_plugin.py
   └── README.md
   ```

2. Implement the plugin class:
   ```python
   from nflaunch.plugins.base import Plugin

   class MyPlugin(Plugin):
       def run(self, job_config):
           # Your plugin logic
           return job_config
   ```

3. Register the plugin in `nflaunch/utils/registry.py`:
   ```python
   from nflaunch.plugins.my_plugin.my_plugin import MyPlugin
   # Add to the bottom of the file with other plugin registrations:
   plugin_registry.register("my_plugin", MyPlugin)
   ```

4. Document your plugin in `nflaunch/plugins/my_plugin/README.md`

### Plugin Best Practices

- **Validate inputs early** - Check required options in `__init__`
- **Log informatively** - Use the logger to provide helpful feedback
- **Handle dry-run mode** - Check for dry-run and skip actual operations
- **Document thoroughly** - Provide clear README with examples
- **Test with real data** - Ensure plugin works with actual pipeline requirements

### Example: Simple Plugin

```python
from nflaunch.plugins.base import Plugin
from nflaunch.backends.base import JobConfig

class ExamplePlugin(Plugin):
    def __init__(self, job_config: JobConfig) -> None:
        super().__init__(job_config)

        # Access plugin options from job_config
        plugin_options = self.job_config.plugin_options

        # Validate required options
        required = ["option1", "option2"]
        for key in required:
            if key not in plugin_options:
                raise ValueError(f"Plugin option '{key}' is required")

        self.option1 = plugin_options["option1"]
        self.option2 = plugin_options["option2"]

    def load(self) -> None:
        self.logger.info(f"Running ExamplePlugin with {self.option1}")

        # Modify job_config attributes as needed
        # Note: Modify self.job_config directly, don't return it
        # Example: self.job_config.samplesheet = "/path/to/generated/samplesheet.csv"
```

## Troubleshooting

### Plugin Not Found

If you receive an error that a plugin is not found:

1. Verify the plugin name matches the registered name
2. Check that the plugin is properly imported in `nflaunch/plugins/__init__.py`
3. Ensure the plugin directory contains `__init__.py`

### Plugin Options Validation Error

If plugin options fail validation:

1. Ensure `--plugin-options` contains valid JSON
2. Verify all required options are provided
3. Check the plugin's README for required option names and types

### Dry-Run Behavior

In dry-run mode, plugins should:
- Log what they would do
- Skip actual file operations
- Skip cloud API calls
- Still modify config attributes but log actions instead of performing them

Check the `self.job_config.dry_run` flag in your plugin implementation to handle dry-run appropriately.

## See Also

- [CLI Reference](cli-reference.md) - Plugin-related CLI options
- [Quickstart Guide](quickstart.md) - Examples using plugins
- [Architecture](architecture.md) - Plugin system design
- [oncoanalyser Plugin README](../nflaunch/plugins/oncoanalyser/README.md) - Detailed plugin example
