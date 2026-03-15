# FullDemoWorkflow

A complete demo workflow that orchestrates scaffold and environment tasks.

## Structure

```
workflow-2/
├── config.yaml       # Workflow configuration
├── ix.py             # FullDemoWorkflow implementation
├── scaffold/         # DemoScaffold component
│   ├── config.yaml
│   └── ix.py
├── environment/      # DemoEnvironment component
│   ├── config.yaml
│   └── ix.py
└── tests/            # Unit tests
```

## Usage

```bash
# Dry-run (print YAML)
ix run /path/to/workflow-2 -n argo -s argo-workflow-executor --dry-run

# Submit with custom environment id
ix run /path/to/workflow-2 \
  -n argo \
  -s argo-workflow-executor \
  -p environment.id=my-instance-001 \
  --dry-run

# Submit to Kubernetes
ix run /path/to/workflow-2 \
  -n argo \
  -s argo-workflow-executor \
  --host https://127.0.0.1:40067 \
  --token $ARGO_TOKEN
```

## Components

### DemoScaffold

A minimal scaffold that creates a container task printing environment info.

### DemoEnvironment

A minimal environment that provides mock environment data and a verification task.
