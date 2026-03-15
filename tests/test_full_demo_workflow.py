"""
Unit tests for workflow-2 components.
"""

import pytest
from pathlib import Path

from interaxions.hub import AutoScaffold, AutoEnvironment, AutoWorkflow
from interaxions.schemas import XJob, WorkflowConfig, RuntimeConfig, ScaffoldConfig, EnvironmentConfig
from interaxions.schemas.task import Environment


WORKFLOW_2_PATH = str(Path(__file__).parent.parent)
SCAFFOLD_PATH = str(Path(__file__).parent.parent / "scaffold")
ENVIRONMENT_PATH = str(Path(__file__).parent.parent / "environment")


# ============================================================================
# DemoScaffold Tests
# ============================================================================

class TestDemoScaffoldConfig:
    """Tests for DemoScaffold configuration loading."""

    def test_load_scaffold_from_local_path(self):
        """AutoScaffold can load DemoScaffold from local path."""
        scaffold = AutoScaffold.from_repo(SCAFFOLD_PATH)
        
        assert scaffold is not None
        assert scaffold.config.type == "demo-scaffold"

    def test_scaffold_has_correct_repo_type(self):
        """Scaffold has repo_type='scaffold'."""
        scaffold = AutoScaffold.from_repo(SCAFFOLD_PATH)
        
        assert scaffold.config.repo_type == "scaffold"


class TestDemoScaffoldCreateTask:
    """Tests for DemoScaffold.create_task()."""

    def test_create_task_returns_hera_container(self):
        """create_task returns a valid Hera Container object."""
        from hera.workflows import Container as HeraContainer
        
        scaffold = AutoScaffold.from_repo(SCAFFOLD_PATH)
        
        job = XJob(
            name="test-scaffold",
            workflow=WorkflowConfig(
                repo_name_or_path=WORKFLOW_2_PATH,
                params={},
            ),
            runtime=RuntimeConfig(namespace="default"),
        )
        
        environment = Environment(
            id="test-instance",
            type="demo-environment",
            data={"message": "test data"},
        )
        
        result = scaffold.create_task(job, environment)
        
        assert isinstance(result, HeraContainer)

    def test_create_task_uses_environment_id(self):
        """Script name includes environment id."""
        scaffold = AutoScaffold.from_repo(SCAFFOLD_PATH)
        
        job = XJob(
            name="test-scaffold",
            workflow=WorkflowConfig(
                repo_name_or_path=WORKFLOW_2_PATH,
                params={},
            ),
            runtime=RuntimeConfig(namespace="default"),
        )
        
        environment = Environment(
            id="my-test-instance",
            type="demo-environment",
            data={},
        )
        
        result = scaffold.create_task(job, environment)
        
        assert "my-test-instance" in result.name


# ============================================================================
# DemoEnvironment Tests
# ============================================================================

class TestDemoEnvironmentConfig:
    """Tests for DemoEnvironment configuration loading."""

    def test_load_environment_from_local_path(self):
        """AutoEnvironment can load DemoEnvironment from local path."""
        env = AutoEnvironment.from_repo(ENVIRONMENT_PATH)
        
        assert env is not None
        assert env.config.type == "demo-environment"

    def test_environment_has_correct_repo_type(self):
        """Environment has repo_type='environment'."""
        env = AutoEnvironment.from_repo(ENVIRONMENT_PATH)
        
        assert env.config.repo_type == "environment"


class TestDemoEnvironmentGet:
    """Tests for DemoEnvironment.get()."""

    def test_get_returns_environment_object(self):
        """get() returns an Environment object."""
        env = AutoEnvironment.from_repo(ENVIRONMENT_PATH)
        
        result = env.get("test-instance-001")
        
        assert isinstance(result, Environment)
        assert result.id == "test-instance-001"
        assert result.type == "demo-environment"

    def test_get_returns_data_dict(self):
        """get() returns Environment with data dict."""
        env = AutoEnvironment.from_repo(ENVIRONMENT_PATH)
        
        result = env.get("test-instance-002")
        
        assert isinstance(result.data, dict)
        assert "message" in result.data


class TestDemoEnvironmentCreateTask:
    """Tests for DemoEnvironment.create_task()."""

    def test_create_task_returns_hera_container(self):
        """create_task returns a valid Hera Container object."""
        from hera.workflows import Container as HeraContainer
        
        env = AutoEnvironment.from_repo(ENVIRONMENT_PATH)
        
        job = XJob(
            name="test-environment",
            workflow=WorkflowConfig(
                repo_name_or_path=WORKFLOW_2_PATH,
                params={},
            ),
            runtime=RuntimeConfig(namespace="default"),
        )
        
        environment = env.get("test-instance-003")
        
        result = env.create_task(job, environment)
        
        assert isinstance(result, HeraContainer)


# ============================================================================
# FullDemoWorkflow Tests
# ============================================================================

class TestFullDemoWorkflowConfig:
    """Tests for FullDemoWorkflow configuration loading."""

    def test_load_workflow_from_local_path(self):
        """AutoWorkflow can load FullDemoWorkflow from local path."""
        workflow = AutoWorkflow.from_repo(WORKFLOW_2_PATH)
        
        assert workflow is not None
        assert workflow.config.type == "full-demo"

    def test_workflow_has_correct_repo_type(self):
        """Workflow has repo_type='workflow'."""
        workflow = AutoWorkflow.from_repo(WORKFLOW_2_PATH)
        
        assert workflow.config.repo_type == "workflow"


class TestFullDemoWorkflowCreate:
    """Tests for FullDemoWorkflow.create_workflow()."""

    def test_create_workflow_returns_hera_workflow(self):
        """create_workflow returns a valid Hera Workflow object."""
        from hera.workflows import Workflow as HeraWorkflow
        
        workflow = AutoWorkflow.from_repo(WORKFLOW_2_PATH)
        
        job = XJob(
            name="test-full-demo",
            workflow=WorkflowConfig(
                repo_name_or_path=WORKFLOW_2_PATH,
                params={
                    "scaffold": {
                        "repo_name_or_path": SCAFFOLD_PATH,
                    },
                    "environment": {
                        "repo_name_or_path": ENVIRONMENT_PATH,
                        "id": "demo-instance-001",
                    },
                },
            ),
            runtime=RuntimeConfig(namespace="default"),
        )
        
        result = workflow.create_workflow(job)
        
        assert isinstance(result, HeraWorkflow)

    def test_create_workflow_has_two_tasks(self):
        """Workflow contains scaffold and environment tasks."""
        workflow = AutoWorkflow.from_repo(WORKFLOW_2_PATH)
        
        job = XJob(
            name="test-full-demo",
            workflow=WorkflowConfig(
                repo_name_or_path=WORKFLOW_2_PATH,
                params={
                    "scaffold": {
                        "repo_name_or_path": SCAFFOLD_PATH,
                    },
                    "environment": {
                        "repo_name_or_path": ENVIRONMENT_PATH,
                        "id": "demo-instance-002",
                    },
                },
            ),
            runtime=RuntimeConfig(namespace="default"),
        )
        
        result = workflow.create_workflow(job)
        
        # Should have at least 2 templates (scaffold + environment)
        assert len(result.templates) >= 2

    def test_create_workflow_uses_job_namespace(self):
        """Workflow uses namespace from job.runtime."""
        workflow = AutoWorkflow.from_repo(WORKFLOW_2_PATH)
        
        job = XJob(
            name="test-full-demo",
            workflow=WorkflowConfig(
                repo_name_or_path=WORKFLOW_2_PATH,
                params={
                    "scaffold": {
                        "repo_name_or_path": SCAFFOLD_PATH,
                    },
                    "environment": {
                        "repo_name_or_path": ENVIRONMENT_PATH,
                        "id": "demo-instance-003",
                    },
                },
            ),
            runtime=RuntimeConfig(namespace="test-namespace"),
        )
        
        result = workflow.create_workflow(job)
        
        assert result.namespace == "test-namespace"

    def test_create_workflow_with_empty_params_uses_defaults(self):
        """Workflow uses default scaffold/environment when params not provided."""
        from hera.workflows import Workflow as HeraWorkflow
        
        workflow = AutoWorkflow.from_repo(WORKFLOW_2_PATH)
        
        # No scaffold/environment params provided - should use defaults
        job = XJob(
            name="test-full-demo-defaults",
            workflow=WorkflowConfig(
                repo_name_or_path=WORKFLOW_2_PATH,
                params={},  # Empty params - should use defaults
            ),
            runtime=RuntimeConfig(namespace="default"),
        )
        
        result = workflow.create_workflow(job)
        
        # Should still create a valid workflow
        assert isinstance(result, HeraWorkflow)
        assert len(result.templates) >= 2

    def test_create_workflow_with_only_environment_id_uses_defaults(self):
        """Workflow uses default paths when only environment.id is provided."""
        from hera.workflows import Workflow as HeraWorkflow
        
        workflow = AutoWorkflow.from_repo(WORKFLOW_2_PATH)
        
        # Only provide environment id - should use default paths
        job = XJob(
            name="test-full-demo-partial",
            workflow=WorkflowConfig(
                repo_name_or_path=WORKFLOW_2_PATH,
                params={
                    "environment": {
                        "id": "custom-instance-001",
                    },
                },
            ),
            runtime=RuntimeConfig(namespace="default"),
        )
        
        result = workflow.create_workflow(job)
        
        assert isinstance(result, HeraWorkflow)

    def test_create_workflow_templates_have_script_defined(self):
        """Each task template should have a script definition, not be empty."""
        import yaml
        
        workflow = AutoWorkflow.from_repo(WORKFLOW_2_PATH)
        
        job = XJob(
            name="test-full-demo",
            workflow=WorkflowConfig(
                repo_name_or_path=WORKFLOW_2_PATH,
                params={
                    "scaffold": {
                        "repo_name_or_path": SCAFFOLD_PATH,
                    },
                    "environment": {
                        "repo_name_or_path": ENVIRONMENT_PATH,
                        "id": "demo-instance-script-test",
                    },
                },
            ),
            runtime=RuntimeConfig(namespace="default"),
        )
        
        result = workflow.create_workflow(job)
        yaml_str = result.to_yaml()
        wf_dict = yaml.safe_load(yaml_str)
        
        # Find non-DAG templates (the actual task templates)
        task_templates = [
            t for t in wf_dict["spec"]["templates"]
            if "dag" not in t
        ]
        
        # Each task template should have either 'script', 'container', or 'resource' defined
        for template in task_templates:
            has_executor = any(key in template for key in ["script", "container", "resource", "http"])
            assert has_executor, f"Template '{template['name']}' has no executor (script/container/resource/http). Template: {template}"

    def test_create_workflow_uses_container_template_for_shell_commands(self):
        """Shell commands should use Container template with command/args, not Script."""
        import yaml
        
        workflow = AutoWorkflow.from_repo(WORKFLOW_2_PATH)
        
        job = XJob(
            name="test-full-demo",
            workflow=WorkflowConfig(
                repo_name_or_path=WORKFLOW_2_PATH,
                params={
                    "scaffold": {
                        "repo_name_or_path": SCAFFOLD_PATH,
                    },
                    "environment": {
                        "repo_name_or_path": ENVIRONMENT_PATH,
                        "id": "demo-instance-source-test",
                    },
                },
            ),
            runtime=RuntimeConfig(namespace="default"),
        )
        
        result = workflow.create_workflow(job)
        yaml_str = result.to_yaml()
        wf_dict = yaml.safe_load(yaml_str)
        
        # Find container templates (task executors)
        container_templates = [
            t for t in wf_dict["spec"]["templates"]
            if "container" in t
        ]
        
        # Should have container templates for scaffold and environment tasks
        assert len(container_templates) >= 2, "Should have at least 2 container templates"
        
        for template in container_templates:
            container_def = template["container"]
            # Container should have 'image' field
            assert "image" in container_def, f"Template '{template['name']}' container missing 'image' field"
            # Container should have 'command' field for shell execution
            assert "command" in container_def, f"Template '{template['name']}' container missing 'command' field"
            # Container should have 'args' field with the actual command
            assert "args" in container_def, f"Template '{template['name']}' container missing 'args' field"

    def test_create_workflow_uses_service_account_from_runtime(self):
        """Workflow uses service_account from job.runtime."""
        import yaml
        
        workflow = AutoWorkflow.from_repo(WORKFLOW_2_PATH)
        
        job = XJob(
            name="test-full-demo",
            workflow=WorkflowConfig(
                repo_name_or_path=WORKFLOW_2_PATH,
                params={
                    "environment": {
                        "id": "demo-instance-sa-test",
                    },
                },
            ),
            runtime=RuntimeConfig(
                namespace="test-namespace",
                service_account="argo-workflow-executor",
            ),
        )
        
        result = workflow.create_workflow(job)
        yaml_str = result.to_yaml()
        wf_dict = yaml.safe_load(yaml_str)
        
        # Workflow spec should have serviceAccountName set
        assert "serviceAccountName" in wf_dict["spec"], "Workflow spec missing 'serviceAccountName'"
        assert wf_dict["spec"]["serviceAccountName"] == "argo-workflow-executor"
