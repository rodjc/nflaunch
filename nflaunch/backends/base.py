"""Base classes for backend implementations."""

import os
import random
import string
import uuid
from abc import ABC, abstractmethod
from argparse import Namespace
from collections.abc import Mapping
from dataclasses import dataclass, field
from logging import Logger
from pathlib import Path
from typing import Any

from nflaunch.utils.logger import set_logger
from nflaunch.utils.paths import ensure_directory, resolve_path


def generate_workflowrun_id() -> str:
    """
    Generate a valid Nextflow workflow ID that starts with a lowercase letter.
    """
    uuid_value = str(uuid.uuid4())
    return random.choice(string.ascii_lowercase) + uuid_value[1:]


@dataclass(frozen=True)
class BackendContext:
    """
    Runtime context shared by backend implementations.

    Attributes:
        logger: Logger configured for the backend client.
        tmp_dir: Directory where temporary artifacts are staged prior to upload.
        config_mount_path: Filesystem path inside the runner container where configs mount.
        workflowrun_id: Unique identifier for the Nextflow run.
        job_id: Cloud provider identifier for the runner job.
    """

    logger: Logger
    tmp_dir: Path
    config_mount_path: Path
    workflowrun_id: str
    job_id: str


@dataclass(kw_only=True)
class JobConfig(ABC):
    """
    Base job configuration shared across all cloud providers.
    """

    container_image: str
    backend: str
    base_bucket: str
    remote_cache_path: str
    remote_run_path: str
    workflowrun_id: str = field(default_factory=generate_workflowrun_id)
    pipeline_name: str
    pipeline_version: str
    profile: str
    params_file: str
    config_file: str
    executor_config_file: str
    samplesheet: str
    nextflow_version: str
    sample_id: str | None
    plugin: str
    plugin_options: dict[str, Any] = field(default_factory=dict)
    resume: str
    dry_run: bool
    tmp_dir: str = field(init=False)
    config_mount_path: str = field(init=False)
    job_id: str = field(init=False)

    def __post_init__(self) -> None:
        base_tmp = os.getenv("NF_LAUNCH_TMPDIR") or os.getenv("TMPDIR") or ".tmp"
        tmp_dir = ensure_directory(resolve_path(base_tmp) / self.workflowrun_id)
        self.tmp_dir = str(tmp_dir)

        self.config_mount_path = "/etc/nextflow"
        self.sample_id = self.sample_id or self.workflowrun_id[-8:]
        self.job_id = (
            f"nf-runner-{self.sample_id.replace(',', '-').lower()}-{self.workflowrun_id[:8]}"
        )
        if self.executor_config_file:
            self.executor_config_file = str(resolve_path(self.executor_config_file))
        else:
            self.executor_config_file = str(tmp_dir / "gcp.config")

        pipeline_candidate = self.pipeline_name.strip()
        expanded_pipeline = os.path.expandvars(os.path.expanduser(pipeline_candidate))
        pipeline_path = Path(expanded_pipeline)
        if pipeline_path.exists():
            self.pipeline_name = str(pipeline_path.resolve())


class JobConfigBuilder(ABC):
    """
    Helper class to initialize a `JobConfig` from CLI arguments or mappings.
    """

    @classmethod
    @abstractmethod
    def build(cls, args: Namespace | Mapping[str, Any]) -> JobConfig:
        """
        Load command-line arguments as job configuration attributes.
        """


class BatchClient(ABC):
    """
    Abstract interface for submitting jobs to a cloud batch service.

    Backends receive a `JobConfig` (provider-specific configuration) and a
    `BackendContext` containing derived runtime state (logger, temporary
    directories, workflow identifiers). Implementations should use the context
    where possible to keep business logic independent from JobConfig internals.
    """

    def __init__(self, job_config: JobConfig) -> None:
        from nflaunch.command.nextflow import NextflowCommandBuilder

        self.logger = set_logger(self.__class__.__name__)
        self.job_config = job_config
        self.nxf_cmd_builder = NextflowCommandBuilder(self.job_config)
        self.context = BackendContext(
            logger=self.logger,
            tmp_dir=Path(self.job_config.tmp_dir),
            config_mount_path=Path(self.job_config.config_mount_path),
            workflowrun_id=self.job_config.workflowrun_id,
            job_id=self.job_config.job_id,
        )

    @abstractmethod
    def stage_resources(self) -> None:
        """
        Stage input files and configuration artifacts to cloud storage.
        """

    @abstractmethod
    def launch_job(self) -> None:
        """
        Submit the job to the target cloud batch system.
        """

    @abstractmethod
    def cancel_job(self) -> None:
        """
        Terminate an active cloud batch job.
        """


class FileUploader(ABC):
    """
    Interface for uploading files required by the Nextflow pipeline.
    """

    def __init__(self, job_config: JobConfig) -> None:
        self.logger = set_logger(self.__class__.__name__)
        self.job_config = job_config

    @abstractmethod
    def upload(self, local_path: str) -> None:
        """
        Upload a single file to the remote location defined by the job config.
        """

    @abstractmethod
    def upload_directory(self, directory_path: str, max_workers: int) -> None:
        """
        Upload an entire local pipeline directory to the remote destination.
        """


class ExecutorConfigBuilder(ABC):
    """
    Interface for generating the Nextflow configuration required by the cloud executor.
    """

    def __init__(self, job_config: JobConfig) -> None:
        self.logger = set_logger(self.__class__.__name__)
        self.job_config = job_config

    @abstractmethod
    def build(self) -> None:
        """
        Create the cloud-specific config file in the temporary workspace.

        The resulting file is included in the config list passed to the `-c`
        option of the `nextflow run` command.
        """
