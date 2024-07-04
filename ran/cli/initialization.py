from typing import List, Dict, Union

from state import ran_toml_exists, lockfile_exists
from state import generate_ran_toml
from state import read_lock, produce_lock, apply_lock, RanLock


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
# 2.) (Clone + Compile/Transpile if needed), Package installation. Literally just follow what is desccribed in ran_lock
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
        init_from_ran_toml()
    else:
        if allow_init_from_scratch:
            print("Freshly initializing...")
            full_init_from_scratch()
        else:
            print("Initialization Failed.")


def init_from_lockfile():
    """
    Initialize from lockfile (.ran/ran-lock.json)

    if no ran.toml, also generate that
    """
    # 1.) Find lockfile and make RanLock from it
    ran_lock: RanLock = read_lock()

    # 2.) Run apply_lock(ran_lock)
    apply_lock(ran_lock)

    # 3.) Generate ran.toml if it doesn't exist
    if not ran_toml_exists():
        generate_ran_toml()


def init_from_ran_toml():
    """Initialize from ran.toml"""
    # 1.) Produce RanLock (pre-resolve packages if needed)
    ran_lock: RanLock = produce_lock()

    # 2.) Run apply_lock(ran_lock)
    apply_lock(ran_lock)


# TODO:
def full_init_from_scratch():
    """
    Fully Initialize the project from scratch. By the end, there will be:
    - a ran.toml file
    - .ran/
    - .ran/ran-lock.json
    """
    pass
