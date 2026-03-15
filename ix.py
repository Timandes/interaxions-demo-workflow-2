"""
FullDemoWorkflow - A workflow that orchestrates a scaffold and environment.
"""

import os
from typing import TYPE_CHECKING, Any, Literal, Optional, Dict

from pydantic import BaseModel, Field

from interaxions.workflows.base_workflow import BaseWorkflow, BaseWorkflowConfig
from interaxions.hub import AutoScaffold, AutoEnvironment
from interaxions.schemas import ScaffoldConfig, EnvironmentConfig

if TYPE_CHECKING:
    from hera.workflows import Workflow
    from interaxions.schemas.job import XJob


class PartialScaffoldConfig(BaseModel):
    """Partial scaffold config for flexible user input."""
    repo_name_or_path: Optional[str] = None
    revision: Optional[str] = None
    params: Dict[str, Any] = Field(default_factory=dict)


class PartialEnvironmentConfig(BaseModel):
    """Partial environment config for flexible user input."""
    repo_name_or_path: Optional[str] = None
    id: Optional[str] = None
    revision: Optional[str] = None
    params: Dict[str, Any] = Field(default_factory=dict)


class FullDemoParams(BaseModel):
    """Parameters for FullDemoWorkflow.
    
    All fields are optional - defaults are resolved relative to the workflow directory.
    """
    scaffold: Optional[PartialScaffoldConfig] = None
    environment: Optional[PartialEnvironmentConfig] = None


class FullDemoWorkflowConfig(BaseWorkflowConfig):
    """Configuration for FullDemoWorkflow."""
    type: Literal["full-demo"] = Field(default="full-demo")


class FullDemoWorkflow(BaseWorkflow):
    """A workflow that orchestrates scaffold and environment tasks."""

    config_class = FullDemoWorkflowConfig
    config: FullDemoWorkflowConfig

    def create_workflow(self, job: "XJob", **kwargs: Any) -> "Workflow":
        """Create a workflow with scaffold and environment tasks."""
        from hera.workflows import Workflow, DAG, Task

        # Parse workflow params
        params = FullDemoParams(**job.workflow.params)
        
        # Get the workflow directory from the job's repo_name_or_path
        # This is the original path where the workflow was loaded from
        workflow_dir = os.path.abspath(job.workflow.repo_name_or_path)

        # Resolve scaffold config with defaults
        scaffold_path = os.path.join(workflow_dir, "scaffold")
        scaffold_params = {}
        if params.scaffold:
            if params.scaffold.repo_name_or_path:
                scaffold_path = self._resolve_path(params.scaffold.repo_name_or_path, workflow_dir)
            scaffold_params = params.scaffold.params

        # Resolve environment config with defaults
        env_path = os.path.join(workflow_dir, "environment")
        env_id = "demo-instance"
        env_params = {}
        if params.environment:
            if params.environment.repo_name_or_path:
                env_path = self._resolve_path(params.environment.repo_name_or_path, workflow_dir)
            if params.environment.id:
                env_id = params.environment.id
            env_params = params.environment.params

        # Load components
        scaffold = AutoScaffold.from_repo(scaffold_path)
        env_loader = AutoEnvironment.from_repo(env_path)

        # Get environment data
        environment = env_loader.get(env_id)

        # Create script templates (create_task now returns Script objects)
        scaffold_script = scaffold.create_task(job, environment)
        env_script = env_loader.create_task(job, environment)

        # Build workflow with DAG
        # Scripts are templates that can be referenced by name in tasks
        with Workflow(
            name=f"full-demo-{job.name}",
            namespace=job.runtime.namespace,
            service_account_name=job.runtime.service_account,
            entrypoint="dag",
        ) as wf:
            # Add scripts as templates to the workflow
            # Note: In Hera 5.x, Scripts added to a Workflow context become templates
            
            with DAG(name="dag"):
                # Tasks reference the script templates by name
                scaffold_task = Task(name=scaffold_script.name, template=scaffold_script)
                env_task = Task(name=env_script.name, template=env_script)
                scaffold_task >> env_task

        return wf
    
    def _resolve_path(self, path: str, base_dir: str) -> str:
        """Resolve a path relative to the workflow directory."""
        if os.path.isabs(path):
            return path
        return os.path.normpath(os.path.join(base_dir, path))
