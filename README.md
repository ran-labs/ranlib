# ran

RAN Library

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

This project uses [pixi](https://pixi.sh)

```bash
pixi install
```

### Development

Get started with development environment by running this command:

```bash
pixi shell --change-ps1=false -e dev
```

### Building from source

You must be in the development environment as shown in the command above

```bash
pixi run build
```

In order to install this now, refer to the next section (Local Installation).

### Local Installation

There already exist some pre-built versions with this repo (for now) that can be installed if you have not built them. (We should probably move this to releases). Whether you re-built or not, you can install ran with this command:

```bash
pip install ./ranlib-0.0.1-py3-none-any.whl
```
