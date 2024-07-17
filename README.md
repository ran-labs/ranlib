# ran

RAN Library

NOTE: DELETE `ranlib/ranlib.py` IN PROD

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

This project uses pixi[https://pixi.sh]

```
pixi install
```

### Building from source

First of all, you must have `hatch` installed and probably also want to install pipx
```
pipx install hatch
```

Now, build it. Refer to the next section (Local Installation) in order to install this now.
```
hatch build .
```

### Local Installation

There already exist some pre-built versions with this repo (for now) that can be installed if you have not built them. (We should probably move this to releases). Whether you re-built or not, you can install ran with this command:
```
pip install ./ranlib-0.1.0-py3-none-any.whl
```