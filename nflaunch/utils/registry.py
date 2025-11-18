"""Registry system for backends and plugins."""

from nflaunch.backends.base import BatchClient, JobConfigBuilder
from nflaunch.backends.gcp.batch import GCPBatchClient
from nflaunch.backends.gcp.job import GCPJobConfigBuilder
from nflaunch.plugins.base import Plugin
from nflaunch.plugins.oncoanalyser.oncoanalyser import OncoanalyserPlugin


class BackendRegistry:
    """
    Registry for storing and retrieving backend implementations for batch clients
    and job config builders.

    Resolving backends dynamically enables CLI options such as `--backend google-batch`.
    """

    def __init__(self) -> None:
        self._registry: dict[str, tuple[type[BatchClient], type[JobConfigBuilder]]] = {}

    def register(
        self,
        key: str,
        batch_client_cls: type[BatchClient],
        job_config_builder_cls: type[JobConfigBuilder],
    ) -> None:
        """
        Register a backend implementation in the registry.

        Args:
            key: Identifier for the backend, for example `"google-batch"`.
            batch_client_cls: Concrete `BatchClient` subclass to use.
            job_config_builder_cls: `JobConfigBuilder` subclass responsible for job configs.
        """
        self._registry[key] = (batch_client_cls, job_config_builder_cls)

    def get(self, key: str) -> tuple[type[BatchClient], type[JobConfigBuilder]]:
        """
        Retrieve the registered backend classes for a given key.

        Args:
            key: Backend identifier to look up.

        Returns:
            A tuple containing the batch client class and job config builder class.

        Raises:
            ValueError: The backend key is not registered.
        """
        try:
            return self._registry[key]
        except KeyError:
            available = list(self._registry.keys())
            raise ValueError(f"Unknown backend: '{key}'. Available backends: {available}") from None


class PluginRegistry:
    """
    Registry for storing and retrieving plugin classes by name.

    CLI users can resolve plugins dynamically via arguments such as `--plugin oncoanalyser`.
    """

    def __init__(self) -> None:
        self._registry: dict[str, type[Plugin]] = {}

    def register(self, key: str, cls: type[Plugin]) -> None:
        """
        Register a new plugin class.

        Args:
            key: Unique name for the plugin, for example `"oncoanalyser"`.
            cls: Plugin class implementation to associate with the key.
        """
        self._registry[key] = cls

    def get(self, key: str) -> type[Plugin]:
        """
        Retrieve a registered plugin class by name.

        Args:
            key: Name of the plugin to fetch.

        Returns:
            The plugin class associated with the provided key.

        Raises:
            ValueError: The key is not registered.
        """
        try:
            return self._registry[key]
        except KeyError:
            available = list(self._registry.keys())
            raise ValueError(f"Unknown plugin: '{key}'. Available plugins: {available}") from None


# Initialize registries
backend_registry = BackendRegistry()
plugin_registry = PluginRegistry()

# Register backends
backend_registry.register("google-batch", GCPBatchClient, GCPJobConfigBuilder)

# Register plugins
plugin_registry.register("oncoanalyser", OncoanalyserPlugin)
