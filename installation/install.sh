#!/usr/bin/env bash

echo "Installing RAN..."

cat << EOF | python3 -
import subprocess
import platform


def install_pixi():
    if platform.system() != 'Windows':
        subprocess.run('curl -fsSL https://pixi.sh/install.sh | bash',
            shell=True, check=True)
    else:
        try:
            subprocess.run('iwr -useb https://pixi.sh/install.ps1 | iex',
                shell=True, check=True)
        except subprocess.CalledProcessError:
            subprocess.run('winget install prefix-dev.pixi', shell=True,
                check=True)


def ensure_pixi_installation():
    """Check if pixi is installed and install it if not."""
    try:
        subprocess.run('pixi --version', shell=True, check=True)
    except subprocess.CalledProcessError:
        print('Pixi is not installed. Installing pixi...')
        install_pixi()


def ensure_ranx_installation():
    """Check if RANx is installed (pipx is the preferred method of doing so)"""
    try:
        subprocess.run('ranx ping', shell=True, check=True)
    except subprocess.CalledProcessError:
        print('RANx is not installed. Installing ranx...')
        subprocess.run('pixi global install ranlibx')



import os


def pixi_project_exists() ->bool:
    return os.path.exists('./.pixi') or os.path.exists('./pixi.lock')


def environment_yml_exists():
    if os.path.exists('./environment.yml'):
        return 'environment.yml'
    elif os.path.exists('./environment.yaml'):
        return 'environment.yaml'
    else:
        return None


def semisafe_init_local_pixi_project():
    if pixi_project_exists():
        return
    init_cmd: str = 'pixi init .'
    environment_yml: str = environment_yml_exists()
    if environment_yml:
        print(
            "Conda project detected. Converting to Pixi...(don't worry it's better and easier to use with more functionality)"
            )
        init_cmd += f' --import ./{environment_yml}'
    subprocess.run(init_cmd, shell=True, check=True)


if __name__ == '__main__':
    prerequisites.ensure_pixi_installation()
    prerequisites.ensure_ranx_installation()
    inits.semisafe_init_local_pixi_project()
    subprocess.run('pixi add ranlib', shell=True, check=True)
    subprocess.run('pixi shell --change-ps1=false', shell=True, check=True)
    print(
        "Welcome to the RAN! Type 'exit' once you are finished with this shell"
        )
EOF