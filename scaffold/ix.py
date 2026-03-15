"""
DemoScaffold - A minimal scaffold that prints a message.
"""

from typing import TYPE_CHECKING, Any, Literal

from pydantic import Field

from interaxions.scaffolds.base_scaffold import BaseScaffold, BaseScaffoldConfig

if TYPE_CHECKING:
    from hera.workflows import Container
    from interaxions.schemas.job import XJob
    from interaxions.schemas.task import Environment


class DemoScaffoldConfig(BaseScaffoldConfig):
    """Configuration for DemoScaffold."""
    type: Literal["demo-scaffold"] = Field(default="demo-scaffold")


class DemoScaffold(BaseScaffold):
    """A minimal scaffold for demonstration."""

    config_class = DemoScaffoldConfig
    config: DemoScaffoldConfig

    def create_task(self, job: "XJob", environment: "Environment", **kwargs: Any) -> "Container":
        """Create a container task that prints a message with the environment id."""
        from hera.workflows import Container

        return Container(
            name=f"demo-scaffold-{environment.id}",
            image="busybox",
            command=["sh", "-c"],
            args=[f"echo 'Agent running with env: {environment.id}'"],
        )