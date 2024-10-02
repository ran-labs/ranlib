import functools
import inspect

from ranlib.compilation.compiler import write_exposed_functions  # , exposed_function_buffer
from ranlib.compilation.schemas import RANFunction
from ranlib.constants import PAPER_IMPLEMENTATIONS_BODY_FOLDER_NAME


def infer_paper_id(source_filepath: str) -> str:
    """Infer paper_id via the filepath of a .py file by checking its directory substring"""

    root: str = PAPER_IMPLEMENTATIONS_BODY_FOLDER_NAME + "/"

    paper_id_and_beyond: str = source_filepath[source_filepath.index(root) + len(root) :]

    paper_id: str = paper_id_and_beyond[: paper_id_and_beyond.index("/")]

    return paper_id


# @ran.expose
def expose(func):
    """
    There is ZERO overhead when calling a function decorated with @ran.expose
    """

    # On WRAPPING, add to the exposed_function_buffer

    # Get the source filepath to infer the paper_id
    source_filepath: str = inspect.getsourcefile(func)
    paper_id: str = infer_paper_id(source_filepath)

    # print("EXPOSE FUNCTION NAME:")
    # print(func.__name__)

    # Get the module name of where the function was imported from
    module_name: str = inspect.getmodule(func).__name__

    # Get the function name
    function_name: str = func.__name__

    # Inspect the parameters
    sig = inspect.signature(func)
    params = sig.parameters
    params_str: str = ", ".join([str(value) for name, value in params.items()])

    # Make the function
    ran_function: RANFunction = RANFunction(
        module_name=module_name, function_name=function_name, params_str=params_str
    )

    # Combine to update the JSON
    write_exposed_functions({paper_id: [ran_function]})

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)

        return result

    return wrapper
