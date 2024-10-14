pipelines = [
  {
    name = "fmt-n-lint"
    steps = [
      {
        name     = "format"
        commands = ["pixi run ruff format ranlib"]
      },
      {
        name     = "lint"
        commands = ["pixi run ruff check ranlib --fix"]
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
        commands = ["pixi run bashify installation/install.template.sh"]
      }
    ]
    triggers = [{
      branches = ["main", "dev"]
      actions = ["pre-commit", "manual"]
    }]
  }
]
