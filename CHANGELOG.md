# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [0.2.1] - 2026-04-16

### Fixed
- Runner job now uses standard VM provisioning (the `--spot` flag no longer affects runner VM type)

### Added
- Extended default GCP job labels with pipeline_name and pipeline_version (in addition to workflowrun_id)

## [0.2.0] - 2025-11-23

### Added
- Environment variable support for Google Cloud configuration to reduce command-line verbosity:
  - `NFL_GCP_PROJECT_ID` - Google Cloud project ID
  - `NFL_GCP_REGION` - Google Cloud region
  - `NFL_GCP_SERVICE_ACCOUNT` - Service account email
  - `NFL_GCP_NETWORK` - VPC network name
  - `NFL_GCP_SUBNETWORK` - Subnetwork name
  - `NFL_GCP_BASE_BUCKET` - Base GCS bucket
- Environment variable documentation in GCP Setup guide with usage examples
- Example script demonstrating both environment variable and CLI argument usage

### Changed
- All GCP configuration arguments now support environment variables with CLI argument override capability
- Updated cloud resources documentation with correct GCS structure and lifecycle policies

### Fixed
- Corrected `get_latest_file` method to properly use project_id parameter

## [0.1.1] - 2025-11-19

### Fixed
- `tomli` library dependency update
- Documentation improvements: corrected plugin interface method, fixed class names in architecture docs, added missing repository layout folders
- Installation guide updates: added PyPI installation instructions and README badge

## [0.1.0] - 2025-11-17

### Added
- Initial release of nflaunch
- **Google Cloud Platform Support**: Full integration with Google Cloud Batch for running Nextflow pipelines
- **Plugin System**: Extensible architecture for pipeline-specific customizations
- **CLI Interface**: Comprehensive command-line tool with parameter validation and help documentation
- **Oncoanalyser Plugin**: Pre-configured support for oncoanalyser pipeline
- **Cloud Storage Integration**: Automatic handling of GCS paths and bucket management
