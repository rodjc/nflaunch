"""Tests for CLI validators."""

import argparse
from unittest.mock import MagicMock

import pytest

from nflaunch.cli.validator import Validator


class TestServiceAccountEmail:
    """Tests for sa_email validator."""

    def test_accepts_none(self):
        """Validator should accept None and return None."""
        result = Validator.sa_email(None)
        assert result is None

    def test_accepts_valid_email(self):
        """Validator should accept valid service account emails."""
        valid_emails = [
            "my-service-account@my-project.iam.gserviceaccount.com",
            "test@test-project.iam.gserviceaccount.com",
            "sa-name@project-id-123.iam.gserviceaccount.com",
        ]
        for email in valid_emails:
            result = Validator.sa_email(email)
            assert result == email

    def test_rejects_invalid_format(self):
        """Validator should reject emails that don't match the service account pattern."""
        invalid_emails = [
            "invalid-email@gmail.com",
            "missing-suffix@my-project.com",
            "@my-project.iam.gserviceaccount.com",  # Missing name
            "name@.iam.gserviceaccount.com",  # Missing project
            "name@project",  # Missing domain
            "Name@project.iam.gserviceaccount.com",  # Uppercase not allowed
            "name@Project.iam.gserviceaccount.com",  # Uppercase not allowed
        ]
        for email in invalid_emails:
            with pytest.raises(argparse.ArgumentTypeError):
                Validator.sa_email(email)


class TestBucketName:
    """Tests for bucket_name validator."""

    def test_accepts_none(self):
        """Validator should accept None and return None."""
        result = Validator.bucket_name(None)
        assert result is None

    def test_strips_gs_prefix(self):
        """Validator should strip gs:// prefix from bucket names."""
        assert Validator.bucket_name("gs://my-bucket") == "my-bucket"
        assert Validator.bucket_name("gs://another-bucket") == "another-bucket"

    def test_accepts_plain_bucket_name(self):
        """Validator should accept plain bucket names without prefix."""
        assert Validator.bucket_name("my-bucket") == "my-bucket"
        assert Validator.bucket_name("test-bucket-123") == "test-bucket-123"

    def test_rejects_empty_bucket(self):
        """Validator should reject empty bucket names."""
        with pytest.raises(argparse.ArgumentTypeError, match="cannot be empty"):
            Validator.bucket_name("")
        with pytest.raises(argparse.ArgumentTypeError, match="cannot be empty"):
            Validator.bucket_name("gs://")


class TestJsonObj:
    """Tests for json_obj validator."""

    def test_parses_valid_json_object(self):
        """Validator should parse valid JSON objects."""
        result = Validator.json_obj('{"key": "value"}')
        assert result == {"key": "value"}

        result = Validator.json_obj('{"a": 1, "b": 2}')
        assert result == {"a": 1, "b": 2}

    def test_rejects_invalid_json(self):
        """Validator should reject malformed JSON."""
        with pytest.raises(argparse.ArgumentTypeError, match="Invalid JSON"):
            Validator.json_obj("{invalid}")

    def test_rejects_non_object_json(self):
        """Validator should reject JSON that is not an object."""
        with pytest.raises(argparse.ArgumentTypeError, match="Expected a JSON object"):
            Validator.json_obj('["array", "not", "object"]')

        with pytest.raises(argparse.ArgumentTypeError, match="Expected a JSON object"):
            Validator.json_obj('"just a string"')


class TestPositiveInt:
    """Tests for positive_int validator."""

    def test_accepts_positive_integers(self):
        """Validator should accept positive integers."""
        assert Validator.positive_int("1") == 1
        assert Validator.positive_int("42") == 42
        assert Validator.positive_int("1000") == 1000
        assert Validator.positive_int(5) == 5

    def test_rejects_zero(self):
        """Validator should reject zero."""
        with pytest.raises(argparse.ArgumentTypeError, match="must be greater than zero"):
            Validator.positive_int("0")

    def test_rejects_negative_numbers(self):
        """Validator should reject negative numbers."""
        with pytest.raises(argparse.ArgumentTypeError, match="must be greater than zero"):
            Validator.positive_int("-1")

    def test_rejects_non_numeric(self):
        """Validator should reject non-numeric input."""
        with pytest.raises(argparse.ArgumentTypeError, match="Expected a positive integer"):
            Validator.positive_int("abc")


class TestBackendAliases:
    """Tests for backend_aliases validator."""

    def test_accepts_canonical_name(self):
        """Validator should accept the canonical backend name."""
        assert Validator.backend_aliases("google-batch") == "google-batch"

    def test_accepts_alias(self):
        """Validator should accept known aliases."""
        assert Validator.backend_aliases("gcp-batch") == "google-batch"

    def test_case_insensitive(self):
        """Validator should be case insensitive."""
        assert Validator.backend_aliases("GOOGLE-BATCH") == "google-batch"
        assert Validator.backend_aliases("GCP-Batch") == "google-batch"

    def test_rejects_unknown_backend(self):
        """Validator should reject unknown backend names."""
        with pytest.raises(argparse.ArgumentTypeError, match="Backend must be"):
            Validator.backend_aliases("aws-batch")


class TestBucketUri:
    """Tests for bucket_uri validator."""

    def test_identifies_gcs_uris(self):
        """Validator should identify GCS URIs."""
        assert Validator.bucket_uri("gs://my-bucket") is True
        assert Validator.bucket_uri("gs://my-bucket/path/to/file") is True

    def test_rejects_non_gcs_uris(self):
        """Validator should reject non-GCS URIs."""
        assert Validator.bucket_uri("my-bucket") is False
        assert Validator.bucket_uri("s3://aws-bucket") is False
        assert Validator.bucket_uri("/local/path") is False


class TestValidateRequiredFields:
    """Tests for validate_required_fields method."""

    def test_all_fields_present_via_cli(self):
        """Should not raise error when all required fields are provided via CLI."""
        args = argparse.Namespace(
            base_bucket="my-bucket",
            project_id="my-project",
            region="us-central1",
            service_account_email="sa@my-project.iam.gserviceaccount.com",
            network="default",
            subnetwork="default",
            pipeline_name="nf-core/rnaseq",
        )
        parser = MagicMock()

        # Should not raise any exception
        Validator.validate_required_fields(args, parser)
        parser.error.assert_not_called()

    def test_missing_base_bucket(self):
        """Should raise error when base_bucket is missing."""
        args = argparse.Namespace(
            base_bucket=None,
            project_id="my-project",
            region="us-central1",
            service_account_email="sa@my-project.iam.gserviceaccount.com",
            network="default",
            subnetwork="default",
            pipeline_name="nf-core/rnaseq",
        )
        parser = MagicMock()

        Validator.validate_required_fields(args, parser)
        parser.error.assert_called_once()
        error_msg = parser.error.call_args[0][0]
        assert "--base-bucket is required" in error_msg
        assert "NFL_GCP_BASE_BUCKET" in error_msg

    def test_missing_project_id(self):
        """Should raise error when project_id is missing."""
        args = argparse.Namespace(
            base_bucket="my-bucket",
            project_id=None,
            region="us-central1",
            service_account_email="sa@my-project.iam.gserviceaccount.com",
            network="default",
            subnetwork="default",
            pipeline_name="nf-core/rnaseq",
        )
        parser = MagicMock()

        Validator.validate_required_fields(args, parser)
        parser.error.assert_called_once()
        error_msg = parser.error.call_args[0][0]
        assert "--project-id is required" in error_msg
        assert "NFL_GCP_PROJECT_ID" in error_msg

    def test_missing_pipeline_name(self):
        """Should raise error when pipeline_name is missing (no env var available)."""
        args = argparse.Namespace(
            base_bucket="my-bucket",
            project_id="my-project",
            region="us-central1",
            service_account_email="sa@my-project.iam.gserviceaccount.com",
            network="default",
            subnetwork="default",
            pipeline_name=None,
        )
        parser = MagicMock()

        Validator.validate_required_fields(args, parser)
        parser.error.assert_called_once()
        error_msg = parser.error.call_args[0][0]
        assert "--pipeline-name is required" in error_msg
        # Should not mention environment variable since none exists for pipeline_name
        assert (
            "NFL_GCP" not in error_msg
            or "environment variable" not in error_msg.split("--pipeline-name")[1].split("\n")[0]
        )

    def test_multiple_missing_fields(self):
        """Should report all missing fields in a single error message."""
        args = argparse.Namespace(
            base_bucket=None,
            project_id=None,
            region="us-central1",
            service_account_email="sa@my-project.iam.gserviceaccount.com",
            network=None,
            subnetwork="default",
            pipeline_name=None,
        )
        parser = MagicMock()

        Validator.validate_required_fields(args, parser)
        parser.error.assert_called_once()
        error_msg = parser.error.call_args[0][0]

        # All missing fields should be mentioned
        assert "--base-bucket is required" in error_msg
        assert "--project-id is required" in error_msg
        assert "--network is required" in error_msg
        assert "--pipeline-name is required" in error_msg

    def test_empty_string_treated_as_missing(self):
        """Should treat empty strings as missing values."""
        args = argparse.Namespace(
            base_bucket="",
            project_id="my-project",
            region="us-central1",
            service_account_email="sa@my-project.iam.gserviceaccount.com",
            network="default",
            subnetwork="default",
            pipeline_name="nf-core/rnaseq",
        )
        parser = MagicMock()

        Validator.validate_required_fields(args, parser)
        parser.error.assert_called_once()
        error_msg = parser.error.call_args[0][0]
        assert "--base-bucket is required" in error_msg
