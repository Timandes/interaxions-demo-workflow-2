"""
DemoEnvironment - A minimal environment for demonstration.
"""

from typing import TYPE_CHECKING, Any, Literal

from pydantic import Field

from interaxions.environments.base_environment import BaseEnvironment, BaseEnvironmentConfig
from interaxions.schemas.task import Environment

if TYPE_CHECKING:
    from hera.workflows import Container
    from interaxions.schemas.job import XJob


class DemoEnvironmentConfig(BaseEnvironmentConfig):
    """Configuration for DemoEnvironment."""
    type: Literal["demo-environment"] = Field(default="demo-environment")


class DemoEnvironment(BaseEnvironment):
    """A minimal environment for demonstration."""

    config_class = DemoEnvironmentConfig
    config: DemoEnvironmentConfig

    def get(self, id: str, **kwargs: Any) -> Environment:
        """Return a mock Environment object."""
        return Environment(
            id=id,
            type=self.config.type,
            data={
                "message": f"Demo environment for {id}",
            },
        )

    def create_task(self, job: "XJob", environment: Environment, **kwargs: Any) -> "Container":
        """Create a verification container task."""
        from hera.workflows import Container

        return Container(
            name=f"demo-env-{environment.id}",
            image="busybox",
            command=["sh", "-c"],
            args=[f"echo 'Environment verified: {environment.id}'"],
        )