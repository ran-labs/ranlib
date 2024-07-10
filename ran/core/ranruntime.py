from typing import List, Dict, Tuple, Set

import functools
import inspect

from compilation.compiler import exposed_function_buffer
from compilation.schemas import RANFunction


def infer_paper_id(source_filepath: str) -> str:
    root: str = "_lib/"

    paper_id_and_beyond: str = source_filepath[
        source_filepath.index(root) + len(root) :
    ]

    paper_id: str = paper_id_and_beyond[: paper_id_and_beyond.index("/")]

    return paper_id


# @ran.expose
def expose(func):
    # On WRAPPING, add to the exposed_function_buffer

    # Get the source filepath to infer the paper_id
    source_filepath: str = inspect.getsourcefile(func)
    paper_id: str = infer_paper_id(source_filepath)

    # Get the module name
    module_name: str = inspect.getmodule(func).module_name

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

    # The exposed_function_buffer by default already starts with empty lists for each paper_id, so no need to check
    ran_functions_buffer: List[RANFunction] = exposed_function_buffer[paper_id]

    # Only add if it's not already added
    if ran_function not in ran_functions_buffer:
        ran_functions_buffer.append(ran_function)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)

        return result

    return wrapper
