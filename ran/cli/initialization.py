from typing import List, Dict, Union

from state import ran_toml_exists, lockfile_exists
from state import generate_lockfile, RanLock


# NOTE:Initialization consists of:
# Setting up the project (ran.toml and lockfile will exist)
# Generating a RanLock, either via the lockfile (preferred) or ran.toml
# Pre-Resolve and Install the dependencies of the paper
# Fetch git urls from DB using the RanLock
# git clone them & remove everything that doesnt really matter
# Compile if needed into .ran/ran_modules
# Add it to ran.toml dependencies


# Simplified:
# 1.) Produce lock (pre-resolve packages if needed)
# 2.) (Clone + Compile/Transpile if needed), Package installation
# 3.) Update ran.toml dependencies and lockfile


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
    # Find lockfile and make RanLock from it
    # Then, run init_from_lock(ran_lock)
    # Generate ran.toml if it doesn't exist
    pass


# TODO:
def init_from_lock(lock: RanLock):
    pass


# TODO:
def init_from_rantoml():
    """Initialize from ran.toml"""
    # This adds the extra step at the beginning to produce a lock
    # Make a RanLock then run init_from_lock
    # Write to lockfile
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
