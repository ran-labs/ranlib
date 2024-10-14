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
        name = "update"
        commands = ["bashify installation/install.template.sh"]
      }
    ]
    triggers = [{
      branches = ["main", "dev"]
      actions = ["pre-commit", "manual"]
    }]
  }
]
