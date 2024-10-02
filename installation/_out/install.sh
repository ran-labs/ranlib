#!/usr/bin/env bash

echo "Installing RAN..."

cat << EOF | python3 -
import subprocess


def ensure_pixi_installation():
    """Check if pixi is installed and install it if not."""
    try:
        subprocess.run('pixi --version', shell=True, check=True)
    except subprocess.CalledProcessError:
        print('Pixi is not installed. Installing pixi...')
        subprocess.run('curl -fsSL https://pixi.sh/install.sh | bash',
            shell=True, check=True)


def ensure_ranx_installation():
    """Check if RANx is installed (pipx is the preferred method of doing so)"""
    try:
        subprocess.run('ranx ping', shell=True, check=True)
    except subprocess.CalledProcessError:
        print('RANx is not installed. Installing ranx...')
        subprocess.run('pixi global install ranlibx')


if __name__ == '__main__':
    prerequisites.ensure_pixi_installation()
    prerequisites.ensure_ranx_installation()
EOF