"""These are strictly for EXTERNAL purposes. Do not use them from within ranlib"""

import os
import subprocess


def pixi_project_exists() -> bool:
    return os.path.exists("./.pixi") or os.path.exists("./pixi.lock")


def environment_yml_exists():
    if os.path.exists("./environment.yml"):
        return "environment.yml"
    elif os.path.exists("./environment.yaml"):
        return "environment.yaml"
    else:
        return None


def semisafe_init_local_pixi_project():
    # Check whether there is one already. if so, return
    if pixi_project_exists():
        return

    # Initialize a pixi project
    init_cmd: str = "pixi init ."
    environment_yml: str = environment_yml_exists()
    if environment_yml:
        print(
            "Conda project detected. Converting to Pixi...(don't worry it's better and easier to use with more functionality)"
        )
        init_cmd += f" --import ./{environment_yml}"

    subprocess.run(init_cmd, shell=True, check=True)
