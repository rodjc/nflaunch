"""Abstract base classes for workflow command builders."""

from abc import ABC, abstractmethod

from nflaunch.backends.base import JobConfig
from nflaunch.utils.logger import set_logger


class CommandBuilder(ABC):
    """
    Abstract base class for building workflow execution commands.

    Implementations construct the command-line invocation string for a given workflow engine
    (currently Nextflow), keeping the launcher engine-agnostic and extensible.
    """

    def __init__(self, job_config: JobConfig) -> None:
        """
        Initialize the command builder with the active job configuration.

        Args:
            job_config: Job configuration used to render the command string.
        """
        self.logger = set_logger(self.__class__.__name__)
        self.job_config = job_config

    @abstractmethod
    def build(self) -> str:
        """
        Construct the complete command-line string needed to run the workflow.

        Returns:
            A shell-compatible command string.
        """
