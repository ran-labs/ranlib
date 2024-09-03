import subprocess
from ranlib._external import install_checks as prerequisites


if __name__ == "__main__":
    # First, go thru the prerequisites
    
    # Pixi
    prerequisites.check_pixi_installation()
    
    # pipX
    prerequisites.check_pipx_installation()
    
    # RANx
    prerequisites.check_ranx_installation()

    # Main RAN installation
    # TODO: 
