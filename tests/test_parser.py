"""Tests for CLI argument parser."""

import os
from unittest.mock import patch

import pytest

from nflaunch.cli.parser import parse_args


class TestEnvironmentVariables:
    """Tests for environment variable support in CLI parser."""

    @patch("sys.argv", ["nflaunch", "--pipeline-name", "test"])
    def test_env_vars_used_when_cli_args_not_provided(self):
        """Environment variables should be used as defaults when CLI args are omitted."""
        env_vars = {
            "NFL_GCP_PROJECT_ID": "env-project",
            "NFL_GCP_REGION": "env-region",
            "NFL_GCP_SERVICE_ACCOUNT": "sa@env-project.iam.gserviceaccount.com",
            "NFL_GCP_NETWORK": "env-network",
            "NFL_GCP_SUBNETWORK": "env-subnetwork",
            "NFL_GCP_BASE_BUCKET": "env-bucket",
        }

        with patch.dict(os.environ, env_vars, clear=False):
            args = parse_args()

            assert args.project_id == "env-project"
            assert args.region == "env-region"
            assert args.service_account_email == "sa@env-project.iam.gserviceaccount.com"
            assert args.network == "env-network"
            assert args.subnetwork == "env-subnetwork"
            assert args.base_bucket == "env-bucket"

    @patch(
        "sys.argv",
        [
            "nflaunch",
            "--pipeline-name",
            "test",
            "--project-id",
            "cli-project",
            "--region",
            "cli-region",
            "--service-account-email",
            "sa@cli-project.iam.gserviceaccount.com",
            "--network",
            "cli-network",
            "--subnetwork",
            "cli-subnetwork",
            "--base-bucket",
            "cli-bucket",
        ],
    )
    def test_cli_args_override_env_vars(self):
        """CLI arguments should take precedence over environment variables."""
        env_vars = {
            "NFL_GCP_PROJECT_ID": "env-project",
            "NFL_GCP_REGION": "env-region",
            "NFL_GCP_SERVICE_ACCOUNT": "sa@env-project.iam.gserviceaccount.com",
            "NFL_GCP_NETWORK": "env-network",
            "NFL_GCP_SUBNETWORK": "env-subnetwork",
            "NFL_GCP_BASE_BUCKET": "env-bucket",
        }

        with patch.dict(os.environ, env_vars, clear=False):
            args = parse_args()

            # CLI values should override environment variables
            assert args.project_id == "cli-project"
            assert args.region == "cli-region"
            assert args.service_account_email == "sa@cli-project.iam.gserviceaccount.com"
            assert args.network == "cli-network"
            assert args.subnetwork == "cli-subnetwork"
            assert args.base_bucket == "cli-bucket"

    @patch(
        "sys.argv",
        [
            "nflaunch",
            "--pipeline-name",
            "test",
            "--project-id",
            "cli-project",
            "--service-account-email",
            "sa@cli-project.iam.gserviceaccount.com",
            "--network",
            "cli-network",
        ],
    )
    def test_mixed_cli_and_env_vars(self):
        """Should accept a mix of CLI arguments and environment variables."""
        env_vars = {
            "NFL_GCP_REGION": "env-region",
            "NFL_GCP_SUBNETWORK": "env-subnetwork",
            "NFL_GCP_BASE_BUCKET": "env-bucket",
        }

        with patch.dict(os.environ, env_vars, clear=False):
            args = parse_args()

            # CLI values
            assert args.project_id == "cli-project"
            assert args.service_account_email == "sa@cli-project.iam.gserviceaccount.com"
            assert args.network == "cli-network"

            # Env var values
            assert args.region == "env-region"
            assert args.subnetwork == "env-subnetwork"
            assert args.base_bucket == "env-bucket"

    @patch("sys.argv", ["nflaunch", "--pipeline-name", "test"])
    def test_missing_required_field_raises_error(self):
        """Should raise error when required field is missing from both CLI and env vars."""
        # Clear any existing environment variables
        env_to_clear = [
            "NFL_GCP_PROJECT_ID",
            "NFL_GCP_REGION",
            "NFL_GCP_SERVICE_ACCOUNT",
            "NFL_GCP_NETWORK",
            "NFL_GCP_SUBNETWORK",
            "NFL_GCP_BASE_BUCKET",
        ]

        with patch.dict(os.environ, {}, clear=False):
            for var in env_to_clear:
                os.environ.pop(var, None)

            with pytest.raises(SystemExit):
                parse_args()

    @patch("sys.argv", ["nflaunch", "--pipeline-name", "test"])
    def test_base_bucket_strips_gs_prefix_from_env_var(self):
        """Bucket name validator should strip gs:// prefix from env var values."""
        env_vars = {
            "NFL_GCP_PROJECT_ID": "test-project",
            "NFL_GCP_REGION": "us-central1",
            "NFL_GCP_SERVICE_ACCOUNT": "sa@test-project.iam.gserviceaccount.com",
            "NFL_GCP_NETWORK": "default",
            "NFL_GCP_SUBNETWORK": "default",
            "NFL_GCP_BASE_BUCKET": "gs://my-bucket",
        }

        with patch.dict(os.environ, env_vars, clear=False):
            args = parse_args()

            # gs:// prefix should be stripped by validator
            assert args.base_bucket == "my-bucket"


class TestDefaultValues:
    """Tests for default argument values."""

    @patch(
        "sys.argv",
        [
            "nflaunch",
            "--pipeline-name",
            "test",
            "--project-id",
            "test-project",
            "--region",
            "us-central1",
            "--service-account-email",
            "sa@test-project.iam.gserviceaccount.com",
            "--network",
            "default",
            "--subnetwork",
            "default",
            "--base-bucket",
            "test-bucket",
        ],
    )
    def test_default_backend(self):
        """Default backend should be google-batch."""
        with patch.dict(os.environ, {}, clear=False):
            args = parse_args()
            assert args.backend == "google-batch"

    @patch(
        "sys.argv",
        [
            "nflaunch",
            "--pipeline-name",
            "test",
            "--project-id",
            "test-project",
            "--region",
            "us-central1",
            "--service-account-email",
            "sa@test-project.iam.gserviceaccount.com",
            "--network",
            "default",
            "--subnetwork",
            "default",
            "--base-bucket",
            "test-bucket",
        ],
    )
    def test_default_container_image(self):
        """Default container image should be nextflow/nextflow."""
        with patch.dict(os.environ, {}, clear=False):
            args = parse_args()
            assert args.container_image == "nextflow/nextflow"

    @patch(
        "sys.argv",
        [
            "nflaunch",
            "--pipeline-name",
            "test",
            "--project-id",
            "test-project",
            "--region",
            "us-central1",
            "--service-account-email",
            "sa@test-project.iam.gserviceaccount.com",
            "--network",
            "default",
            "--subnetwork",
            "default",
            "--base-bucket",
            "test-bucket",
        ],
    )
    def test_default_nextflow_version(self):
        """Default Nextflow version should be 25.04.6."""
        with patch.dict(os.environ, {}, clear=False):
            args = parse_args()
            assert args.nextflow_version == "25.04.6"

    @patch(
        "sys.argv",
        [
            "nflaunch",
            "--pipeline-name",
            "test",
            "--project-id",
            "test-project",
            "--region",
            "us-central1",
            "--service-account-email",
            "sa@test-project.iam.gserviceaccount.com",
            "--network",
            "default",
            "--subnetwork",
            "default",
            "--base-bucket",
            "test-bucket",
        ],
    )
    def test_default_spot_instances_enabled(self):
        """Spot instances should be enabled by default."""
        with patch.dict(os.environ, {}, clear=False):
            args = parse_args()
            assert args.spot is True


class TestValidatorIntegration:
    """Tests for validator integration in parser."""

    @patch(
        "sys.argv",
        [
            "nflaunch",
            "--pipeline-name",
            "test",
            "--project-id",
            "test-project",
            "--region",
            "us-central1",
            "--service-account-email",
            "invalid-email",
            "--network",
            "default",
            "--subnetwork",
            "default",
            "--base-bucket",
            "test-bucket",
        ],
    )
    def test_invalid_service_account_email_raises_error(self):
        """Invalid service account email should raise error during parsing."""
        with patch.dict(os.environ, {}, clear=False):
            with pytest.raises(SystemExit):
                parse_args()

    @patch(
        "sys.argv",
        [
            "nflaunch",
            "--pipeline-name",
            "test",
            "--project-id",
            "test-project",
            "--region",
            "us-central1",
            "--service-account-email",
            "sa@test-project.iam.gserviceaccount.com",
            "--network",
            "default",
            "--subnetwork",
            "default",
            "--base-bucket",
            "",
        ],
    )
    def test_empty_base_bucket_raises_error(self):
        """Empty base bucket should raise error during parsing."""
        with patch.dict(os.environ, {}, clear=False):
            with pytest.raises(SystemExit):
                parse_args()

    @patch(
        "sys.argv",
        [
            "nflaunch",
            "--pipeline-name",
            "test",
            "--project-id",
            "test-project",
            "--region",
            "us-central1",
            "--service-account-email",
            "sa@test-project.iam.gserviceaccount.com",
            "--network",
            "default",
            "--subnetwork",
            "default",
            "--base-bucket",
            "test-bucket",
            "--cpu-milli",
            "0",
        ],
    )
    def test_zero_cpu_milli_raises_error(self):
        """Zero CPU milli should raise error (must be positive)."""
        with patch.dict(os.environ, {}, clear=False):
            with pytest.raises(SystemExit):
                parse_args()

    @patch(
        "sys.argv",
        [
            "nflaunch",
            "--pipeline-name",
            "test",
            "--project-id",
            "test-project",
            "--region",
            "us-central1",
            "--service-account-email",
            "sa@test-project.iam.gserviceaccount.com",
            "--network",
            "default",
            "--subnetwork",
            "default",
            "--base-bucket",
            "test-bucket",
            "--backend",
            "aws-batch",
        ],
    )
    def test_invalid_backend_raises_error(self):
        """Invalid backend should raise error during parsing."""
        with patch.dict(os.environ, {}, clear=False):
            with pytest.raises(SystemExit):
                parse_args()


class TestOptionalArguments:
    """Tests for optional arguments."""

    @patch(
        "sys.argv",
        [
            "nflaunch",
            "--pipeline-name",
            "test",
            "--project-id",
            "test-project",
            "--region",
            "us-central1",
            "--service-account-email",
            "sa@test-project.iam.gserviceaccount.com",
            "--network",
            "default",
            "--subnetwork",
            "default",
            "--base-bucket",
            "test-bucket",
            "--dry-run",
        ],
    )
    def test_dry_run_flag(self):
        """Dry run flag should be set when provided."""
        with patch.dict(os.environ, {}, clear=False):
            args = parse_args()
            assert args.dry_run is True

    @patch(
        "sys.argv",
        [
            "nflaunch",
            "--pipeline-name",
            "test",
            "--project-id",
            "test-project",
            "--region",
            "us-central1",
            "--service-account-email",
            "sa@test-project.iam.gserviceaccount.com",
            "--network",
            "default",
            "--subnetwork",
            "default",
            "--base-bucket",
            "test-bucket",
            "--sample-id",
            "SAMPLE_001",
        ],
    )
    def test_sample_id(self):
        """Sample ID should be set when provided."""
        with patch.dict(os.environ, {}, clear=False):
            args = parse_args()
            assert args.sample_id == "SAMPLE_001"

    @patch(
        "sys.argv",
        [
            "nflaunch",
            "--pipeline-name",
            "test",
            "--project-id",
            "test-project",
            "--region",
            "us-central1",
            "--service-account-email",
            "sa@test-project.iam.gserviceaccount.com",
            "--network",
            "default",
            "--subnetwork",
            "default",
            "--base-bucket",
            "test-bucket",
            "--labels",
            '{"team": "oncology", "project": "research"}',
        ],
    )
    def test_labels_json_parsing(self):
        """Labels should be parsed from JSON string."""
        with patch.dict(os.environ, {}, clear=False):
            args = parse_args()
            assert args.labels == {"team": "oncology", "project": "research"}
