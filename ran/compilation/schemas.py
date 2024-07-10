from typing import List, Dict, Set, Union, Tuple
from pydantic import BaseModel, Field


# NOTE: dynamic importing may not be needed since we already have the correct format for modules


class RANFunction(BaseModel):
    module_name: str  # example: "compilation.schemas"
    function_name: str
    params_str: str

    def get_verbose_function_name(self) -> str:
        # Make the module name python-friendly
        safe_module_name: str = self.module_name.replace(".", "___")

        return f"{safe_module_name}__{self.function_name}"

    def as_import_statement(self) -> str:
        return f"from {self.module_name} import {self.function_name}"
