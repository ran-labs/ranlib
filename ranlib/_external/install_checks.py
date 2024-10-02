import subprocess


# Pixi
def ensure_pixi_installation():
    """Check if pixi is installed and install it if not."""
    try:
        subprocess.run("pixi --version", shell=True, check=True)
    except subprocess.CalledProcessError:
        print("Pixi is not installed. Installing pixi...")

        # Install pixi
        subprocess.run("curl -fsSL https://pixi.sh/install.sh | bash", shell=True, check=True)

        # Also installs the autocompletion for the respective shell
        # Maybe remove this if it becomes a problem
        # subprocess.run('eval "$(pixi completion --shell bash)"', shell=True, check=True)
        # subprocess.run('eval "$(pixi completion --shell zsh)"', shell=True, check=True)
        # subprocess.run(
        #     'eval "$(pixi completion --shell fish | source)"',
        #     shell=True,
        #     check=True,
        # )
        # subprocess.run(
        #     'eval "$(pixi completion --shell elvish | slurp)"',
        #     shell=True,
        #     check=True,
        # )


# ranx
def ensure_ranx_installation():
    """Check if RANx is installed (pipx is the preferred method of doing so)"""
    try:
        subprocess.run("ranx ping", shell=True, check=True)
    except subprocess.CalledProcessError:
        print("RANx is not installed. Installing ranx...")
        subprocess.run("pixi global install ranlibx")
