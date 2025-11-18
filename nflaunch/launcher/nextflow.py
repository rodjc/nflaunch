"""Nextflow pipeline launcher orchestrating backend and plugin initialization."""

import json
from argparse import Namespace

from nflaunch.utils.logger import set_logger
from nflaunch.utils.registry import backend_registry, plugin_registry


class NextflowLauncher:
    """
    Launch a Nextflow pipeline on supported cloud providers.
    """

    def __init__(self, args: Namespace) -> None:
        """
        Initialize the launcher with parsed CLI arguments.

        Args:
            args: Parsed namespace returned by the CLI parser.
        """
        self.logger = set_logger(self.__class__.__name__)
        self.args = args

    def run(self) -> None:
        """
        Launch the Nextflow pipeline using the configured batch client.
        """
        self.logger.info("Starting Nextflow Launcher ...")

        _BatchClient, _JobConfigBuilder = backend_registry.get(self.args.backend)
        self.logger.info(f"Backend to use: {_BatchClient.__name__}, {_JobConfigBuilder.__name__}")

        job_config = _JobConfigBuilder.build(self.args)
        job_config_file = f"{job_config.tmp_dir}/job_config.json"
        with open(job_config_file, "w") as f:
            json.dump(job_config.__dict__, f, indent=2)
        self.logger.info(f"Job config loaded from args: {job_config_file}")

        batch_client = _BatchClient(job_config)

        if self.args.plugin:
            _Plugin = plugin_registry.get(self.args.plugin)
            plugin = _Plugin(job_config)
            plugin.load()

        batch_client.stage_resources()
        batch_client.launch_job()
