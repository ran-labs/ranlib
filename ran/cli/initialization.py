from typing import List, Dict, Optional, Union

from state import ran_toml_exists, lockfile_exists


def smart_init(allow_init_from_scratch: bool = True):
    """
    - if .ran/ran-lock.json, install from there
    - else if ran.toml, install from there
    - else, full init from scratch (if allowed)

    Reflect each of these options in the logs
    """

    if lockfile_exists():
        print("Initializing from lockfile...")
        init_from_lockfile()
    elif ran_toml_exists():
        print("Initializing from ran.toml...")
        init_from_rantoml()
    else:
        if allow_init_from_scratch:
            print("Freshly initializing...")
            full_init_from_scratch()
        else:
            print("Initialization Failed.")


# TODO:
def init_from_lockfile():
    """
    Initialize from lockfile (.ran/ran-lock.json)

    if no ran.toml, also generate that
    """
    pass


# TODO:
def init_from_rantoml():
    """Initialize from ran.toml"""
    pass


# TODO:
def full_init_from_scratch():
    """
    Fully Initialize the project from scratch. By the end, there will be:
    - a ran.toml file
    - .ran/
    - .ran/ran-lock.json
    """
    pass
