from pydantic import BaseModel, Field

from ranlib.__init__ import __version__
from ranlib.state.pathutils import get_dotran_dir_path

RANLIB_VERSION_PREFIX: str = "RANLib Version "


class RANFILE(BaseModel):
    version: str = __version__
    python_dependencies: list[str] = Field(default=[])

    def write_to_ranfile(self):
        dotran_dir_path: str = get_dotran_dir_path()

        ranfile_str: str = f"{RANLIB_VERSION_PREFIX}{self.version}"

        if len(self.python_dependencies) > 0:
            ranfile_str += "\nPython Package Dependencies:\n" + "\n".join(self.python_dependencies)

        with open(f"{dotran_dir_path}/RANFILE", "w") as ranfile:
            ranfile.write(ranfile_str)

    def parse_ranfile(ranfile_str: str, include_version: bool = True):
        """Parse the string into a RANFILE"""
        ranfile: RANFILE = RANFILE()

        lines: list[str] = ranfile_str.splitlines()

        if include_version:
            version_str: str = lines[0]
            ranfile.version = version_str[len(RANLIB_VERSION_PREFIX) :]

        if len(lines) <= 2:
            return ranfile

        # Line 0 = version
        # Line 1 = 'Python Package Dependencies'
        ranfile.python_dependencies = lines[2:]

        return ranfile


def read_ranfile(dotran_dir_path: str = None, include_version: bool = True) -> RANFILE:
    if dotran_dir_path is None:
        dotran_dir_path = get_dotran_dir_path()

    ranfile_str: str = ""
    with open(f"{dotran_dir_path}/RANFILE", "r") as file:
        ranfile_str = file.read()

    ranfile: RANFILE = RANFILE.parse_ranfile(ranfile_str, include_version=include_version)
    return ranfile
