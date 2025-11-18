"""Validators and type converters for command-line arguments."""

import argparse
import json
import os
import re

from nflaunch.utils.paths import resolve_path


class Validator:
    """
    Collection of argparse-compatible validators and normalizers.
    """

    @staticmethod
    def sa_email(email: str) -> str:
        """
        Validate a service account email address.

        Args:
            email: Candidate email address.

        Returns:
            The original email if valid.

        Raises:
            argparse.ArgumentTypeError: The email is not a valid service account address.
        """
        # Simpler user-managed SA pattern: name@PROJECT_ID.iam.gserviceaccount.com
        # name/project: start with a letter; then [a-z0-9-]*
        GSA_USER_MANAGED_RE = re.compile(
            r"^(?P<name>[a-z][a-z0-9-]*)@(?P<project>[a-z][a-z0-9-]*)\.iam\.gserviceaccount\.com$"
        )

        try:
            if not GSA_USER_MANAGED_RE.match(email or ""):
                raise ValueError(
                    "Invalid service account email. Expected 'name@PROJECT_ID.iam.gserviceaccount.com'"
                )
            return email
        except ValueError as err:
            raise argparse.ArgumentTypeError(str(err)) from err

    @staticmethod
    def json_obj(s: str) -> dict:
        """
        Parse a JSON string and ensure it is a JSON object.

        Args:
            s: JSON string supplied on the command line.

        Returns:
            Parsed dictionary representing the JSON object.

        Raises:
            argparse.ArgumentTypeError: The string is not valid JSON or not an object.
        """
        try:
            val = json.loads(s)
        except json.JSONDecodeError as err:
            raise argparse.ArgumentTypeError(f"Invalid JSON: {err}") from err
        if not isinstance(val, dict):
            raise argparse.ArgumentTypeError('Expected a JSON object (e.g., \'{"key": "value"}\').')
        return val

    @staticmethod
    def positive_int(value: str | int) -> int:
        """
        Ensure the provided value is a positive integer (> 0).

        Args:
            value: String or integer supplied on the command line.

        Returns:
            The parsed integer.

        Raises:
            argparse.ArgumentTypeError: The value is missing, non-numeric, or non-positive.
        """
        try:
            n = int(value)
        except (TypeError, ValueError) as err:
            raise argparse.ArgumentTypeError(
                f"Expected a positive integer, got: {value!r}"
            ) from err
        if n <= 0:
            raise argparse.ArgumentTypeError("Value must be greater than zero.")
        return n

    @staticmethod
    def backend_aliases(s: str) -> str:
        """
        Accept known backend aliases and normalize to the canonical name.

        Args:
            s: Backend identifier from user input.

        Returns:
            Canonical backend name.

        Raises:
            argparse.ArgumentTypeError: The alias is not recognized.
        """
        s = s.lower()
        aliases = {
            "google-batch": "google-batch",
            "gcp-batch": "google-batch",
        }
        if s in aliases:
            return aliases[s]
        raise argparse.ArgumentTypeError("Backend must be 'google-batch' (alias: 'gcp-batch').")

    @staticmethod
    def bucket_name(bucket: str) -> str:
        """
        Accept `my-bucket` or `gs://my-bucket` and return `my-bucket`.

        Args:
            bucket: Bucket identifier from the CLI.

        Returns:
            Bucket name without scheme or trailing slashes.

        Raises:
            argparse.ArgumentTypeError: The bucket is empty after normalization.
        """
        b = bucket.split("/")[-1]
        if not b:
            raise argparse.ArgumentTypeError("Base bucket cannot be empty.")
        return b

    @staticmethod
    def bucket_uri(s: str) -> bool:
        """
        Return True when the string looks like a GCS URI.
        """
        return s.startswith("gs://")

    @staticmethod
    def clip_upload_workers(n: int | None) -> int:
        """
        Interpret None or non-positive values as CPU-count auto detection.

        Args:
            n: Requested number of workers.

        Returns:
            Number of workers to use, never less than one.
        """
        max_cpu = os.cpu_count()
        if n is None or n <= 0:
            return max_cpu  # type: ignore
        return n

    @staticmethod
    def existing_path(value: str) -> str:
        """
        Ensure the supplied value points to an existing filesystem path.

        Leading and trailing whitespace is stripped, environment variables are expanded, and the
        resulting path is returned in absolute form.

        Args:
            value: Path argument supplied on the command line.

        Returns:
            Normalized absolute path, or an empty string when the value is None.

        Raises:
            argparse.ArgumentTypeError: The path does not exist.
        """
        if value is None:
            return ""
        s = str(value).strip()
        # Expand ~ and env vars, then absolutize
        abs_path = resolve_path(s)
        if not abs_path.exists():
            raise argparse.ArgumentTypeError(f"Path does not exist: {s}")
        return str(abs_path)
