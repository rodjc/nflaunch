"""Google Cloud Batch client implementation for job submission."""

from pathlib import Path

from google.cloud import batch_v1

from nflaunch.backends.base import BatchClient
from nflaunch.backends.gcp.file import GCPExecutorConfigBuilder, GCPFileUploader
from nflaunch.backends.gcp.job import GCPJobConfig


class GCPBatchClient(BatchClient):
    """
    Submit `GCPJobConfig` executions through the `google-cloud-batch` API.
    """

    job_config: GCPJobConfig

    def __init__(self, job_config: GCPJobConfig) -> None:
        super().__init__(job_config)

    def stage_resources(self) -> None:
        """
        Generate the executor config and upload all required artifacts to GCS.
        """
        executor_config = GCPExecutorConfigBuilder(self.job_config)
        executor_config.build()

        file_uploader = GCPFileUploader(self.job_config)
        for local_file in [
            file
            for file in [
                self.job_config.config_file,
                self.job_config.params_file,
                self.job_config.samplesheet,
                self.job_config.executor_config_file,
            ]
            if file
        ]:
            file_uploader.upload(local_file)

        if self.job_config.pipeline_name.endswith(".nf"):
            file_uploader.upload(self.job_config.pipeline_name)

        pipeline_path = Path(self.job_config.pipeline_name)
        if pipeline_path.is_dir():
            file_uploader.upload_directory(
                str(pipeline_path.resolve()), max_workers=self.job_config.upload_max_workers
            )

    def launch_job(self) -> None:
        """
        Submit the configured Google Cloud Batch job or emit the dry-run request.
        """
        # Volume configuration
        gcs_bucket = batch_v1.GCS(
            remote_path=f"{self.job_config.remote_run_path}/{self.job_config.workflowrun_id}"
        )
        gcs_volume = batch_v1.Volume(
            gcs=gcs_bucket,
            mount_path=str(self.context.config_mount_path),
        )

        nxf_cmd = self.nxf_cmd_builder.build()

        # Define the container runnable
        image_uri = self.job_config.container_image
        if ":" not in image_uri:
            image_uri = f"{image_uri}:{self.job_config.nextflow_version}"

        container = batch_v1.Runnable.Container(
            image_uri=image_uri, entrypoint="/bin/bash", commands=["-c", nxf_cmd]
        )
        runnable = batch_v1.Runnable(container=container)

        # Jobs can be divided into tasks. In this case, we have only one task.
        compute_resource = batch_v1.ComputeResource(
            cpu_milli=self.job_config.cpu_milli, memory_mib=self.job_config.memory_mib
        )
        task = batch_v1.TaskSpec(
            runnables=[runnable],
            volumes=[gcs_volume],
            # max_run_duration="86400s", # 24hs
            compute_resource=compute_resource,
        )
        group = batch_v1.TaskGroup(task_count=1, task_spec=task)

        # VM settings
        provisioning_model = (
            batch_v1.AllocationPolicy.ProvisioningModel.SPOT
            if self.job_config.spot
            else batch_v1.AllocationPolicy.ProvisioningModel.STANDARD
        )
        instance_policy = batch_v1.AllocationPolicy.InstancePolicy(
            machine_type=self.job_config.machine_type,
            provisioning_model=provisioning_model,
        )
        instance_template = batch_v1.AllocationPolicy.InstancePolicyOrTemplate(
            policy=instance_policy
        )

        # Network settings
        network_interface = batch_v1.AllocationPolicy.NetworkInterface(
            no_external_ip_address=self.job_config.use_private_address,
        )
        if self.job_config.network:
            network_interface.network = self.job_config.network
        if self.job_config.subnetwork:
            network_interface.subnetwork = self.job_config.subnetwork
        network_policy = batch_v1.AllocationPolicy.NetworkPolicy(
            network_interfaces=[network_interface]
        )

        # Final allocation policy
        allocation_policy = batch_v1.AllocationPolicy(
            instances=[instance_template],
            network=network_policy,
            service_account=batch_v1.ServiceAccount(email=self.job_config.service_account_email),
        )

        # Job definition
        logs_policy = batch_v1.LogsPolicy(destination=batch_v1.LogsPolicy.Destination.CLOUD_LOGGING)
        labels = self.job_config.labels

        job = batch_v1.Job(
            task_groups=[group],
            allocation_policy=allocation_policy,
            logs_policy=logs_policy,
            labels=labels,
        )

        job_id = self.job_config.job_id

        job_request = batch_v1.CreateJobRequest(
            job=job,
            job_id=job_id,
            parent=f"projects/{self.job_config.project_id}/locations/{self.job_config.region}",
        )

        job_request_file = self.context.tmp_dir / "job_request.txt"
        job_logs_url = (
            "https://console.cloud.google.com/batch/jobsDetail/"
            f"regions/{self.job_config.region}/jobs/{job_id}/logs?"
        )
        job_status_cmd = (
            "gcloud batch jobs describe "
            f"--location={self.job_config.region} {job_id} | grep 'state:'"
        )
        job_cancel_cmd = "gcloud batch jobs cancel " f"--location={self.job_config.region} {job_id}"

        if self.job_config.dry_run:
            with open(job_request_file, "w") as f:
                f.write(str(job_request))
                self.logger.info(
                    f"[DRY-RUN] Will submit the following job request: {job_request_file}"
                )
            return None

        client = batch_v1.BatchServiceClient()

        response = client.create_job(job_request)
        with open(job_request_file, "w") as f:
            f.write(str(response))
            self.logger.info(f"Job request submitted: {job_request_file}")
            self.logger.info(f"Job logs:   {job_logs_url}")
            self.logger.info(f"Job status: {job_status_cmd}")
            self.logger.info(f"Cancel job: {job_cancel_cmd}")

    def cancel_job(self) -> None:
        """
        Cancel a running job (not implemented for the GCP backend).
        """
        raise NotImplementedError
