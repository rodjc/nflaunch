from abc import ABC, abstractmethod

from nflaunch.backends.base import JobConfig
from nflaunch.utils.logger import set_logger


class Plugin(ABC):
    """
    Base interface for nflaunch plugins that augment job configuration.
    """

    def __init__(self, job_config: JobConfig) -> None:
        """
        Initialize the plugin with the active job configuration.

        Args:
            job_config: The job configuration associated with the current run.
        """
        self.logger = set_logger(self.__class__.__name__)
        self.job_config = job_config

    @abstractmethod
    def load(self) -> None:
        """
        Load and apply plugin-specific configuration data.
        """
