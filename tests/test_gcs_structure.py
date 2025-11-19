"""Tests for GCS file structure and upload logic."""

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from nflaunch.backends.gcp.file import GCPFileUploader


@pytest.fixture
def mock_job_config():
    """Create a mock GCPJobConfig for testing."""
    config = MagicMock()
    config.remote_run_path = "my-bucket/run"
    config.workflowrun_id = "test-workflow-123"
    config.params_file = "/local/params.yaml"
    config.samplesheet = "/local/samplesheet.csv"
    config.dry_run = False
    return config


def test_config_files_uploaded_to_config_subdirectory(mock_job_config):
    """Test that executor and custom config files are uploaded to /config/ subdirectory."""
    uploader = GCPFileUploader(mock_job_config)

    with patch("nflaunch.backends.gcp.file.storage.Client") as mock_client:
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob

        # Upload a config file (not params or samplesheet)
        config_file = "/local/custom.config"
        uploader.upload(config_file)

        # Verify the blob path includes /config/ subdirectory
        expected_path = "run/test-workflow-123/config/custom.config"
        mock_bucket.blob.assert_called_once_with(expected_path)
        mock_blob.upload_from_filename.assert_called_once_with(config_file)


def test_input_files_uploaded_to_input_subdirectory(mock_job_config):
    """Test that params and samplesheet files are uploaded to /input/ subdirectory."""
    uploader = GCPFileUploader(mock_job_config)

    with patch("nflaunch.backends.gcp.file.storage.Client") as mock_client:
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob

        # Upload params file
        uploader.upload(mock_job_config.params_file)

        # Verify the blob path includes /input/ subdirectory
        expected_path = "run/test-workflow-123/input/params.yaml"
        mock_bucket.blob.assert_called_with(expected_path)

        # Upload samplesheet
        uploader.upload(mock_job_config.samplesheet)

        # Verify the blob path includes /input/ subdirectory
        expected_path = "run/test-workflow-123/input/samplesheet.csv"
        mock_bucket.blob.assert_called_with(expected_path)


def test_nextflow_log_path_mapping(mock_job_config):
    """Test that nextflow log path maps to /etc/nextflow/logs/nextflow.log."""
    from nflaunch.command.nextflow import NextflowCommandBuilder

    mock_job_config.config_mount_path = "/etc/nextflow"
    mock_job_config.pipeline = "nf-core/rnaseq"
    mock_job_config.revision = "3.14.0"
    mock_job_config.params_file = "/etc/nextflow/input/params.yaml"
    mock_job_config.samplesheet = None
    mock_job_config.executor_config_file = "/etc/nextflow/config/executor.config"
    mock_job_config.custom_config_file = None
    mock_job_config.pipeline_dir = None
    mock_job_config.resume = None

    builder = NextflowCommandBuilder(mock_job_config)
    command = builder.build()

    # Verify log path is set correctly
    assert "-log /etc/nextflow/logs/nextflow.log" in command


def test_pipeline_directory_uploaded_to_config(mock_job_config):
    """Test that pipeline directories are uploaded to /config/ subdirectory."""
    uploader = GCPFileUploader(mock_job_config)

    with (
        patch("nflaunch.backends.gcp.file.storage.Client") as mock_client,
        patch("nflaunch.backends.gcp.file.transfer_manager") as mock_transfer,
        patch("nflaunch.backends.gcp.file.iter_directory_files") as mock_iter,
        patch("nflaunch.backends.gcp.file.relative_paths") as mock_rel_paths,
        patch("nflaunch.backends.gcp.file.Path") as mock_path_class,
    ):
        mock_bucket = Mock()
        mock_client.return_value.bucket.return_value = mock_bucket

        # Mock Path to return a directory that exists
        mock_path = Mock()
        mock_path.is_dir.return_value = True
        mock_path.name = "pipeline"
        mock_path_class.return_value.resolve.return_value = mock_path

        # Mock directory structure
        mock_iter.return_value = [Path("/local/pipeline/main.nf")]
        mock_rel_paths.return_value = [Path("main.nf")]
        mock_transfer.upload_many_from_filenames.return_value = [None]

        uploader.upload_directory("/local/pipeline", max_workers=4)

        # Verify blob prefix includes /config/ subdirectory
        expected_prefix = "run/test-workflow-123/config/pipeline/"
        mock_transfer.upload_many_from_filenames.assert_called_once()
        call_kwargs = mock_transfer.upload_many_from_filenames.call_args[1]
        assert call_kwargs["blob_name_prefix"] == expected_prefix


def test_dry_run_mode_logs_without_uploading(mock_job_config):
    """Test that dry run mode logs intended uploads without executing them."""
    mock_job_config.dry_run = True
    uploader = GCPFileUploader(mock_job_config)

    with patch("nflaunch.backends.gcp.file.storage.Client") as mock_client:
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob

        uploader.upload("/local/test.config")

        # Verify no actual upload occurred
        mock_blob.upload_from_filename.assert_not_called()
