import importlib.util
import json
import os
import shutil
import subprocess
import sys

# TODO: use this to write more maintainable code
import textwrap

# from typing import Union
# from pydantic import BaseModel, Field
from pydantic import (
    TypeAdapter,  # for Pydantic V2 (which we are using)
    parse_obj_as,  # for Pydantic V1
)

from ranlib.compilation.abs2relimports import replace_imports
from ranlib.compilation.schemas import RANFunction
from ranlib.constants import (
    DOTRAN_FOLDER_NAME,
    PAPER_IMPLEMENTATIONS_BODY_FOLDER_NAME,
)
from ranlib.state.pathutils import find_root_path, get_dotran_dir_path
from ranlib.utils import find_all_python_files

# The keys are the actual paper_id such as "attention_is_all_you_need"
# This is from .ran/ran-modules/_lib/.comptools/exposed_functions.json
exposed_functions_cache: dict[str, list[RANFunction]] = {}


def read_exposed_functions_from_cache() -> dict[str, list[RANFunction]]:
    if exposed_functions_cache:
        # if not empty, return it
        return exposed_functions_cache

    filepath: str = f"{get_dotran_dir_path()}/{PAPER_IMPLEMENTATIONS_BODY_FOLDER_NAME}/.comptools/exposed_functions.json"

    return read_saved_exposed_functions(filepath)


def convert_buffer_to_serializable(buffer: dict[str, list[RANFunction]]) -> dict[str, list[dict]]:
    buffer_serializable: dict[str, list[dict]] = {}

    for key, val_list in buffer.items():
        buffer_serializable[key] = [val.dict() for val in val_list]

    return buffer_serializable


def combine_buffers(buffer1: dict[str, list], buffer2: dict[str, list]) -> dict[str, list]:
    # Copy buffer1
    combined_buffer: dict[str, list[RANFunction]] = dict(
        buffer1.items()
    )  # {k: v for (k, v) in buffer1.items()}

    for key, value in buffer2.items():
        # key: str
        # value: List[RANFunction]

        combined_list: list[RANFunction] = combined_buffer.get(key)
        if combined_list is None:
            # Set the key if it doesn't exist
            combined_buffer[key] = value
        else:
            # Add all list items if the key already exists
            # No duplicates tho
            combined_buffer[key] = list(frozenset(combined_list).union(frozenset(value)))

    return combined_buffer


def read_saved_exposed_functions(json_filepath: str) -> dict[str, list[RANFunction]]:
    if not os.path.exists(json_filepath):
        # Make a new one
        new_exposed_functions: dict = {}
        with open(json_filepath, "w") as file:
            json.dump(new_exposed_functions, file)

        return new_exposed_functions

    with open(json_filepath, "r") as file:
        # Dict[str, List[Dict]]
        data = json.load(file)

    ta = TypeAdapter(dict[str, list[RANFunction]])
    saved_exposed_functions: dict[str, list[RANFunction]] = ta.validate_python(data)

    return saved_exposed_functions


def write_exposed_functions(exposed_buffer: dict[str, list[RANFunction]]):
    filepath: str = f"{get_dotran_dir_path()}/{PAPER_IMPLEMENTATIONS_BODY_FOLDER_NAME}/.comptools/exposed_functions.json"

    existing_buffer: dict[str, list[RANFunction]] = read_saved_exposed_functions(filepath)

    # Combine the buffers
    combined_buffer: dict[str, list[RANFunction]] = combine_buffers(
        existing_buffer, exposed_buffer
    )

    # Write it to the json file
    exposed_functions_dot_json: dict[str, list[dict]] = convert_buffer_to_serializable(
        combined_buffer
    )
    with open(filepath, "w") as file:
        json.dump(exposed_functions_dot_json, file)


def import_all_pymodules_from_directory(directory: str):
    for file_name in find_all_python_files(directory):
        module_name: str = file_name[
            file_name.index(
                f"{DOTRAN_FOLDER_NAME}/"
            ) : -3  # ignore the .py
        ].replace("/", ".")

        # print(module_name)

        importlib.import_module(module_name)


def delete_redundant_stuff(repo_dir: str):
    print("Removing BS...")
    try:
        # README
        repo_readme_path: str = f"{repo_dir}/README.md"
        if os.path.exists(repo_readme_path):
            os.remove(repo_readme_path)

        # LICENSE
        repo_license_path: str = f"{repo_dir}/LICENSE"
        if os.path.exists(repo_license_path):
            os.remove(repo_license_path)

        # .gitattributes
        repo_gitattributes_path: str = f"{repo_dir}/.gitattributes"
        if os.path.exists(repo_gitattributes_path):
            os.remove(repo_gitattributes_path)

        # .gitignore
        repo_gitignore_path: str = f"{repo_dir}/.gitignore"
        if os.path.exists(repo_gitignore_path):
            os.remove(repo_gitignore_path)
    except OSError as err:
        print(f"OS Error when trying to clean BS: {err}")

    # TODO: anything in the .ranignore


def precompile(to_add_paper_ids: list[str], to_remove_paper_ids: list[str]):
    """Setup the paper_ids to add + Cleanup the ones to remove"""

    dotran_dir_path: str = get_dotran_dir_path()

    # Create _lib directory if it doesn't already exist
    _lib_dir_path: str = f"{dotran_dir_path}/{PAPER_IMPLEMENTATIONS_BODY_FOLDER_NAME}"

    try:
        os.mkdir(_lib_dir_path)
        print(f"Directory '{_lib_dir_path}' created")

        # Make the __init__.py
        with open(f"{_lib_dir_path}/__init__.py", "w") as initfile:
            initfile.write(" ")
    except FileExistsError:
        print(f"Directory '{_lib_dir_path}' already exists")

    # Create .comptools directory if it doesn't already exist
    dotcomptools_dir_path: str = f"{_lib_dir_path}/.comptools"
    try:
        os.mkdir(dotcomptools_dir_path)
        print(f"Directory '{dotcomptools_dir_path}' created")
    except FileExistsError:
        pass
        # print(f"Directory '{_lib_dir_path}' already exists")

    # Cleanup the old to remove
    # Also remove from the existing buffer and rewrite it
    print("Cleaning up trash...")

    existing_filepath: str = f"{_lib_dir_path}/.comptools/exposed_functions.json"

    existing_buffer: dict[str, list[RANFunction]] = read_saved_exposed_functions(existing_filepath)

    existing_buffer_is_not_empty: bool = bool(existing_buffer)

    for paper_id in to_remove_paper_ids:
        folderpath: str = f"{dotran_dir_path}/{PAPER_IMPLEMENTATIONS_BODY_FOLDER_NAME}/{paper_id}"
        modulepath: str = f"{dotran_dir_path}/{paper_id}.py"

        # Remove the folder and module
        try:
            shutil.rmtree(folderpath, ignore_errors=True)
            os.remove(modulepath)
        except OSError as err:
            print(f"OS Error when trying to cleanup paper_ids: {err}")

        # Remove the associated paper_id from the saved function buffer
        if existing_buffer_is_not_empty:
            del existing_buffer[paper_id]

    # Write the updated buffer
    if existing_buffer_is_not_empty:
        print("Writing buffer...")
        existing_buffer_serializable: dict[str, list[dict]] = convert_buffer_to_serializable(
            existing_buffer
        )
        with open(existing_filepath, "w") as file:
            json.dump(existing_buffer_serializable, file)

    # Temporarily add user project root path to the sys path
    project_root_path: str = find_root_path()
    sys.path.append(project_root_path)


def compile(
    paper_id: str, compilation_parent_dir: str, compilation_target_subdir: str
) -> list[str]:
    """
    Returns compilation steps

    compilation_parent_dir - typically the .ran/ran_modules dir
    compilation_target_subdir - typically the folder that the repo was just cloned into, such as `mamba` in the context of .ran/ran_modules/mamba. However, this is NOT the paper_id
    """

    old_repo_dir: str = f"{compilation_parent_dir}/{compilation_target_subdir}"

    # First: delete all the shit that don't matter
    # README.md
    # LICENSE
    # .gitattributes
    # .gitignore
    delete_redundant_stuff(old_repo_dir)

    # Also, rename the directory name to _lib/paper_id/*
    # Maybe move this off of subprocess later (security issue)
    repo_dir: str = f"{compilation_parent_dir}/{PAPER_IMPLEMENTATIONS_BODY_FOLDER_NAME}/{paper_id}"
    # print(f'MOVING "{old_repo_dir}" TO "{repo_dir}"')
    subprocess.run(
        f'mv "{old_repo_dir}" "{repo_dir}"',
        shell=True,
    )

    # Preprocess all python modules into using relative imports for all imports
    replace_imports(repo_dir)

    # Blindly import EVERYTHING (all python modules) in the repo. This will add the functions to exposed_function_buffer
    # There will be a problem when you have stuff like `train.py` with no encapsulating classes/functions and just code
    # In those cases, we can rely on our users to just encapsulate them in functions and do if __name__ == "__main__" if they want to preserve the ability to run as a python file
    # For cases where ppl wont budge on that, we can manually have a prompt-engineered LLM reformat it for them
    import_all_pymodules_from_directory(repo_dir)

    # Generate the python module based off of the stuff in the exposed_function_buffer[paper_id]
    # Includes the import statements (don't need to do dynamic imports rn) as well as the linked functions
    # At this point, exposed_function_buffer[paper_id] is filled up

    exposed_functions_dict: dict[str, list[RANFunction]] = read_exposed_functions_from_cache()
    exposed_functions: list[RANFunction] = exposed_functions_dict[paper_id]

    import_statements_list: list[str] = []
    function_code_list: list[str] = []

    def check_name_conflicts(exposed_function: RANFunction) -> bool:
        for exposed_function_2 in exposed_functions:
            if (
                exposed_function_2 != exposed_function
                and exposed_function.function_name == exposed_function_2.function_name
            ):
                return True

        return False

    for exposed_function in exposed_functions:
        # Generate function name (avoid conflicts)
        imported_func_name: str = ""
        import_statement: str = ""
        if check_name_conflicts(exposed_function):
            imported_func_name = exposed_function.get_verbose_function_name()

            # The +2 is there for the '__'
            imported_func_name = imported_func_name[
                imported_func_name.index(paper_id) + len(paper_id) + 2 :
            ]
        else:
            imported_func_name = exposed_function.function_name

        func_name: str = "" + imported_func_name
        imported_func_name += (
            "_"  # add an _ so the imported function name doesnt conflict with the actual thing
        )

        import_statement = exposed_function.as_import_statement(alias=imported_func_name)

        # Add to import statements
        import_statements_list.append(import_statement)

        # Generate function body (calls the original imported function)
        generated_function_code: str = f"def {func_name}({exposed_function.params_str}):\n\t# Put any desired pre-call handling here\n\t\n\tresult = {imported_func_name}({exposed_function.parse_params_names_only()})\n\t\n\t# Put any desired post-call handling here\n\t\n\treturn result"

        # Add to function_code_list
        function_code_list.append(generated_function_code)

    # Import statements
    import_statements: str = "\n".join(import_statements_list) + "\n"
    functions_str: str = "\n\n\n".join(function_code_list)

    full_python_module_str: str = f"{import_statements}\n\n{functions_str}"

    # Now make the actual python file
    with open(f"{compilation_parent_dir}/{paper_id}.py", "w") as file:
        file.write(full_python_module_str)

    print(f"{paper_id} compilation complete.")

    # Return compilation steps but who gives a fuck rn lmao
    return []


def postcompilation():
    """Postcompilatin of ALL papers"""
    # Clear the cache
    global exposed_functions_cache

    exposed_functions_cache = {}

    # Remove the user project root path after compilation
    sys.path.remove(find_root_path())
