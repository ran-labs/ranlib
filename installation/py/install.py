"""
Context: someone is downloading RAN with `curl -fsSL https://ran.so/install.sh | bash` which just redirects them to here (the bash file, not this python file)

This is not the main way to install RAN, but is a nice touch for people who want to just check it out for the first time
"""

import subprocess
from ranlib._external import install_checks as prerequisites
from ranlib._external import inits


if __name__ == "__main__":
    # First, go thru the prerequisites and ensure they are installed
    
    # Pixi
    prerequisites.ensure_pixi_installation()
    
    # RANx
    prerequisites.ensure_ranx_installation()

    # Main RAN installation
    # ensure pixi project is initialized
    inits.semisafe_init_local_pixi_project()
    
    # install RAN
    subprocess.run("pixi add ranlib", shell=True, check=True)

    # enter RAN shell
    subprocess.run("pixi shell --change-ps1=false", shell=True, check=True)
    print("Welcome to the RAN! Type 'exit' once you are finished with this shell")
