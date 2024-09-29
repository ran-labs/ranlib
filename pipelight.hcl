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
  }
]
