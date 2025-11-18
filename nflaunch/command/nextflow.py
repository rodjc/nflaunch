"""Nextflow command builder for constructing workflow execution commands."""

from pathlib import Path

from nflaunch.command.base import CommandBuilder, JobConfig


class NextflowCommandBuilder(CommandBuilder):
    """
    CommandBuilder implementation for Nextflow workflows.

    Generates the appropriate `nextflow run ...` command based on the provided job configuration,
    including revision, config files, resume options, and profiles.
    """

    def __init__(self, job_config: JobConfig) -> None:
        """
        Initialize the command builder with job configuration.

        Args:
            job_config: Configuration containing pipeline metadata and user-defined parameters.
        """
        super().__init__(job_config)

    def build(self) -> str:
        """
        Construct a Nextflow command suitable for running in a cloud environment.

        Returns:
            The shell command to execute the pipeline.
        """
        self.logger.info("Building Nextflow command ...")

        params_filename = (
            Path(self.job_config.params_file).name if self.job_config.params_file else None
        )
        config_filename = (
            Path(self.job_config.config_file).name if self.job_config.config_file else None
        )
        executor_config_filename = Path(self.job_config.executor_config_file).name
        config_mount_path = self.job_config.config_mount_path

        pipeline_path = Path(self.job_config.pipeline_name)
        is_local_pipeline = self.job_config.pipeline_name.endswith(".nf") or pipeline_path.is_dir()

        # Build the base command - only include -revision for remote pipelines
        if is_local_pipeline:
            nxf_base_cmd = [
                "nextflow",
                f"-log {config_mount_path}/logs/nextflow.log",
                f"run {self.job_config.pipeline_name}",
                f"-c {config_mount_path}/config/{executor_config_filename}",
                f"-name {self.job_config.workflowrun_id}",
            ]
        else:
            nxf_base_cmd = [
                "nextflow",
                f"-log {config_mount_path}/logs/nextflow.log",
                f"run {self.job_config.pipeline_name} -revision {self.job_config.pipeline_version}",
                f"-c {config_mount_path}/config/{executor_config_filename}",
                f"-name {self.job_config.workflowrun_id}",
            ]

        if self.job_config.pipeline_name.endswith(".nf"):
            workflow_filename = pipeline_path.name
            nxf_base_cmd[2] = f"run {config_mount_path}/config/{workflow_filename}"

        if pipeline_path.is_dir():
            directory_name = pipeline_path.name
            nxf_base_cmd[0] = f"cd {config_mount_path}/config/{directory_name} && nextflow"
            nxf_base_cmd[2] = "run ."

        if self.job_config.resume:
            try:
                run_name, session_id = self.job_config.resume.split(",")
            except ValueError as err:
                raise ValueError(
                    f"Invalid resume format. Expected 'WORKFLOWRUN_ID,SESSION_ID', got '{self.job_config.resume}'"
                ) from err
            nxf_base_cmd[-1] = f"-name {run_name} -resume {session_id}"

        if config_filename:
            nxf_base_cmd.append(f"-c {config_mount_path}/config/{config_filename}")

        if params_filename:
            nxf_base_cmd.append(f"-params-file {config_mount_path}/input/{params_filename}")

        if self.job_config.profile:
            nxf_base_cmd.append(f"-profile {self.job_config.profile}")

        nxf_cmd = " ".join(nxf_base_cmd)

        cache_cmd = (
            f"export NXF_CLOUDCACHE_PATH=gs://{self.job_config.remote_cache_path} "
            "&& export NXF_IGNORE_RESUME_HISTORY=true"
        )

        return " && ".join([cache_cmd, nxf_cmd])
