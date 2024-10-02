# ran

RAN Library (more info coming soon)

## Philosophy & Tenants

For any paper:

- EASY install
- EASY use
- EASY upload

- No BS
- No strings attached
- No extra setup needed

Just drop-in and start using it

## Info for Users

- Users of ranlib who use other papers will have to use pixi (setup is automatic)
- However, if all you wanna do is publish your implementation of a paper, pixi will try to be as invisible as possible

## Setup

Prerequisites: this project uses [pixi](https://pixi.sh) and [pipelight](https://pipelight.dev)

```bash
pixi install
pixi run -e dev setup  # runs `pipelight enable git-hooks` under the hood (MANDATORY)
```

### Development

Get started with development environment by running this command:

```bash
pixi shell --change-ps1=false -e dev
```

During development, you can actually test the `ran` CLI command via just running `ran`!

### Creating Releases

1. After committing your code changes, change the version of `pyproject.toml` accordingly.
2. RUN `scripts/update-version.sh` (it will make an update version commit and push on your behalf--don't worry)

### Building from source

You must be in the development environment as shown in the command above

```bash
pixi run build
```

