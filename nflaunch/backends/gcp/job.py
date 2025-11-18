"""Google Cloud Platform job configuration and builder."""

import os
from argparse import Namespace
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from nflaunch.backends.base import JobConfig, JobConfigBuilder


@dataclass(kw_only=True)
class GCPJobConfig(JobConfig):
    """
    GCP-specific job configuration extending the common job configuration.

    Attributes:
        project_id: GCP project identifier.
        region: Region where the Batch job runs.
        service_account_email: Service account email used by Batch.
        network: VPC network name or resource path.
        subnetwork: Subnetwork name or resource path.
    """

    project_id: str
    region: str
    service_account_email: str
    network: str | None
    subnetwork: str | None
    use_private_address: bool
    spot: bool
    labels: dict[str, str]
    upload_max_workers: int
    machine_type: str | None = None
    cpu_milli: int | None = None
    memory_mib: int | None = None

    def __post_init__(self) -> None:
        super().__post_init__()
        cpu_count = os.cpu_count() or 1
        self.upload_max_workers = self.upload_max_workers or cpu_count
        self.remote_cache_path = self.remote_cache_path or f"{self.base_bucket}/cache"
        self.remote_run_path = self.remote_run_path or f"{self.base_bucket}/run"
        self.labels = self.labels or {}
        self.labels["workflowrun_id"] = self.workflowrun_id
        self.cpu_milli = self.cpu_milli or 2000
        self.memory_mib = self.memory_mib or 2000
        self.machine_type = self.machine_type or "e2-small"


class GCPJobConfigBuilder(JobConfigBuilder):
    """
    Construct `GCPJobConfig` objects from CLI arguments or mapping data.
    """

    @classmethod
    def build(cls, args: Namespace | Mapping[str, Any]) -> GCPJobConfig:
        """
        Build a `GCPJobConfig` instance from an argparse namespace or mapping.

        Args:
            args: Parsed arguments or dictionary containing job configuration keys.

        Returns:
            A fully populated `GCPJobConfig`.
        """
        if isinstance(args, Namespace):
            data: dict[str, Any] = vars(args)
        else:
            data = dict(args)

        if data.get("plugin_options") is None:
            data["plugin_options"] = {}
        if data.get("labels") is None:
            data["labels"] = {}
        if "use_private_address" not in data:
            data["use_private_address"] = True

        return GCPJobConfig(**data)
