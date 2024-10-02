import subprocess
from ranlib._external import install_checks as prerequisites


if __name__ == "__main__":
    # First, go thru the prerequisites
    
    # Pixi
    prerequisites.ensure_pixi_installation()
    
    # RANx
    prerequisites.ensure_ranx_installation()

    # Main RAN installation
    # TODO: 
