from typing import Union

from ranlib.state import dotran, ranstate
from ranlib.state.pathutils import lockfile_exists, ran_toml_exists
from ranlib.state.ranstate import RanLock, RanTOML

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


def appears_to_be_initialized() -> bool:
    # TODO: maybe a better metric later?
    return lockfile_exists() and ran_toml_exists()


def smart_init(allow_init_from_scratch: bool = True):
    """
    - if ran/ran-lock.json, install from there
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
    Initialize from lockfile (ran/ran-lock.json)

    if no ran.toml, also generate that
    """
    # 1.) Find lockfile and make RanLock from it
    ran_lock: RanLock = ranstate.read_lock()

    # 2.) Run apply_lock(ran_lock)
    ranstate.apply_lock(ran_lock, from_zero=True)

    # 3.) Generate ran.toml if it doesn't exist
    if not ran_toml_exists():
        ranstate.generate_ran_toml()


def init_from_ran_toml(force_fresh_install: bool = True):
    """Initialize from ran.toml"""
    # 0.) Check if .ran/ was initialized correctly, because in order for a lock to be written that's the condition
    if not lockfile_exists():
        dotran.generate_dotran_dir()

    # 1.) Read RanTOML
    ran_toml: RanTOML = ranstate.read_ran_toml()

    # 2.) Apply RanTOML (we don't want to rewrite it since we are applying the same thing)
    ranstate.apply_ran_toml(ran_toml, from_zero=force_fresh_install, write_to_randottoml=False)


def full_init_from_scratch():
    """
    Fully Initialize the project from scratch. By the end, there will be:
    - a ran.toml file
    - ran/
    - ran/ran-lock.json
    """
    # Generate the ran/ directory with the ran/*ran_modules/
    dotran.generate_dotran_dir()

    # Generate the .ran/ran-lock.json
    ranstate.generate_ran_lock()

    # Generate the ran.toml (make this last)
    ranstate.generate_ran_toml()
