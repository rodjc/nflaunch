"""Google Cloud Storage file operations and executor configuration."""

from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from google.cloud import storage
from google.cloud.storage import transfer_manager

from nflaunch.backends.base import ExecutorConfigBuilder, FileUploader
from nflaunch.backends.gcp.job import GCPJobConfig
from nflaunch.utils.templates import render_template
from nflaunch.utils.upload import iter_directory_files, relative_paths


def parse_gcs_path(gcs_uri: str) -> tuple[str, str]:
    """
    Parse a GCS URI into bucket name and object prefix.

    Args:
        gcs_uri: Path such as `gs://my-bucket/path/to/dir`.

    Returns:
        A tuple of `(bucket_name, object_prefix)`.

    Raises:
        ValueError: The URI does not start with `gs://`.
    """
    if not gcs_uri.startswith("gs://"):
        raise ValueError("Invalid GCS URI: must start with 'gs://'")

    parsed = urlparse(gcs_uri)
    bucket_name = parsed.netloc
    object_prefix = parsed.path.strip("/")

    return bucket_name, object_prefix


def get_latest_file(
    bucket_name: str, bucket_prefix: str, filename_prefix: str | None, filename_extension: str
) -> str:
    """
    Return the most recently updated object within a prefix that matches the extension.

    Args:
        bucket_name: Name of the bucket to inspect.
        bucket_prefix: Object prefix to limit the search.
        filename_prefix: Optional filename prefix filter.
        filename_extension: File extension to match, e.g. `.bam`.

    Returns:
        Fully qualified GCS URI of the latest matching file, or an empty string if none exist.
    """
    client = storage.Client()
    bucket = client.bucket(bucket_name)

    blobs = bucket.list_blobs(prefix=bucket_prefix)

    latest_bam = None
    latest_time = None

    for blob in blobs:
        if blob.name.endswith(filename_extension):
            basename = blob.name.split("/")[-1]
            if filename_prefix is None or basename.startswith(filename_prefix):
                if latest_time is None or blob.updated > latest_time:
                    latest_time = blob.updated
                    latest_bam = blob.name

    if latest_bam:
        return f"gs://{bucket_name}/{latest_bam}"
    else:
        return ""


class GCPFileUploader(FileUploader):
    """
    Google Cloud Storage implementation of the `FileUploader` interface.

    Handles uploads of individual files and entire directories to the paths derived from
    the active `GCPJobConfig`.
    """

    job_config: GCPJobConfig

    def __init__(self, job_config: GCPJobConfig) -> None:
        super().__init__(job_config)

    def upload(self, local_path: str) -> None:
        """
        Upload a single local file to the workflow's staging area in GCS.

        Args:
            local_path: Filesystem path to the file that should be uploaded.

        Raises:
            FileNotFoundError: The file could not be located or read.
            google.api_core.GoogleAPIError: The upload failed due to GCS issues.
        """
        try:
            storage_client = storage.Client()
            bucket_name, prefix = parse_gcs_path("gs://" + self.job_config.remote_run_path)
            bucket = storage_client.bucket(bucket_name)
            file_path = Path(local_path).resolve()
            file_name = file_path.name

            # Determine subdirectory based on file type
            if local_path in [self.job_config.params_file, self.job_config.samplesheet]:
                subdirectory = "input"
            else:
                subdirectory = "config"

            destination_blob = (
                f"{prefix}/{self.job_config.workflowrun_id}/{subdirectory}/{file_name}"
            )
            blob = bucket.blob(destination_blob)

            if self.job_config.dry_run:
                self.logger.info(
                    f"[DRY-RUN] Will upload {file_path.relative_to(file_path.parent.parent)} to gs://{bucket.name}/{destination_blob}"
                )
                return
            blob.upload_from_filename(local_path)
            self.logger.info(
                f"Uploaded {file_path.relative_to(file_path.parent.parent)} to gs://{bucket.name}/{destination_blob}"
            )
        except (FileNotFoundError, OSError, PermissionError) as err:
            self.logger.error(
                f"Failed to access or upload {file_path.relative_to(file_path.parent.parent)}: {err}"
            )
            raise

    def upload_directory(self, directory_path: str, max_workers: int) -> None:
        """
        Upload a local pipeline directory to GCS using the transfer manager.

        Args:
            directory_path: Local directory whose contents should be uploaded.
            max_workers: Maximum worker threads to use for the transfer.

        Raises:
            FileNotFoundError: The directory does not exist.
            google.api_core.GoogleAPIError: One or more uploads failed.
        """
        directory_path_obj = Path(directory_path).resolve()
        if not directory_path_obj.is_dir():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        directory_name = directory_path_obj.name
        file_paths = iter_directory_files(directory_path_obj, exclude_dirs=[".git"])
        rel_paths = relative_paths(file_paths, directory_path_obj)
        string_paths = [str(path) for path in rel_paths]

        if self.job_config.dry_run:
            self.logger.info(
                f"[DRY-RUN] Found {len(string_paths)} files in {directory_path_obj} ready to upload"
            )
        bucket_name, prefix = parse_gcs_path("gs://" + self.job_config.remote_run_path)
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)

        blob_name_prefix = f"{prefix}/{self.job_config.workflowrun_id}/config/{directory_name}/"

        if self.job_config.dry_run:
            self.logger.info(
                f"[DRY-RUN] Will upload {directory_path_obj} to gs://{bucket.name}/{blob_name_prefix}"
            )
            return

        # Start the upload using the transfer manager
        results = transfer_manager.upload_many_from_filenames(
            bucket=bucket,
            blob_name_prefix=blob_name_prefix,
            filenames=string_paths,
            source_directory=str(directory_path_obj),
            max_workers=max_workers,
        )

        for name, result in zip(string_paths, results, strict=True):
            if isinstance(result, Exception):
                self.logger.error(f"Failed to upload {name} due to exception: {result}")
                raise result

        self.logger.info(f"Uploaded {directory_path_obj} to gs://{bucket.name}/{blob_name_prefix}")


class GCPExecutorConfigBuilder(ExecutorConfigBuilder):
    """
    Generate the Nextflow executor configuration file for the Google Cloud Batch backend.

    The template (`gcp.config.template`) is populated with run-specific values and written to
    the temporary directory so it can be provided to Nextflow at runtime.

    Attributes:
        job_config: Configuration object holding project, region, bucket, and label details.
    """

    job_config: GCPJobConfig

    def __init__(self, job_config: GCPJobConfig) -> None:
        super().__init__(job_config)
        self.job_config = job_config

    def build(self) -> None:
        """
        Generate a GCP-specific executor config file and assign it to `executor_config_file`.

        The template variables replaced in `gcp.config.template` include bucket paths, project
        metadata, network configuration, service account email, and resource labels. When
        `dry_run` is enabled no file is written, but the destination path is logged.
        """
        gcp_config_file = self.job_config.executor_config_file

        log_suffix = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Include workflowrun_id in the resource labels
        labels = self.job_config.labels.copy()
        labels["workflowrun_id"] = self.job_config.workflowrun_id
        resource_labels = ", ".join(f'"{k}": "{v}"' for k, v in labels.items())

        template_root = Path(__file__).resolve().parent / "templates"
        template_path = template_root / "gcp.config.template"
        template_extras_path = template_root / "gcp.extras.template"

        # Replace template variables with values from job_config
        config = render_template(
            template_path,
            {
                "base_bucket": self.job_config.base_bucket,
                "remote_run_path": self.job_config.remote_run_path,
                "workflowrun_id": self.job_config.workflowrun_id,
                "log_suffix": log_suffix,
                "project_id": self.job_config.project_id,
                "region": self.job_config.region,
                "use_private_address": str(self.job_config.use_private_address).lower(),
                "spot": str(self.job_config.spot).lower(),
                "network": self.job_config.network or "",
                "subnetwork": self.job_config.subnetwork or "",
                "service_account_email": self.job_config.service_account_email,
                "resource_labels": resource_labels,
            },
        )

        extras_config = template_extras_path.read_text()

        with open(gcp_config_file, "w") as f:
            f.write(config + extras_config)

        if self.job_config.dry_run:
            self.logger.info(f"[DRY-RUN] Will write executor config file {gcp_config_file}")
        else:
            self.logger.info(f"GCP Batch executor config written to: {gcp_config_file}")
