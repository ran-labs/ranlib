pipelines = [
  {
    name = "fmt-n-lint"
    steps = [
      {
        name     = "format"
        commands = ["ruff format ranlib"]
      },
      {
        name     = "lint"
        commands = ["ruff check ranlib --fix"]
      }
    ]
    triggers = [{
      branches = ["main", "dev"]
      actions  = ["pre-commit", "manual"]
    }]
  },
  {
    name = "update-install-sh"
    steps = [
      {
        name = "update-hooks"
        commands = ["python3 ./prebuild.py"]
      }
    ]
    triggers = [{
      branches = ["main", "dev"]
      actions = ["pre-commit", "manual"]
    }]
  }
]
