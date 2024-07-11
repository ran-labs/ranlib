from typing import List, Dict, Set, Union, Tuple
from pydantic import BaseModel, Field


# NOTE: dynamic importing may not be needed since we already have the correct format for modules


class RANFunction(BaseModel):
    module_name: str  # example: "compilation.schemas"
    function_name: str
    params_str: str

    def get_verbose_function_name(self) -> str:
        # Make the module name python-friendly
        safe_module_name: str = self.module_name.replace(".", "__")

        return f"{safe_module_name}__{self.function_name}"

    def as_import_statement(self, prefix: str = "", alias: str = "") -> str:
        stmt: str = f"from {prefix}{self.module_name} import {self.function_name}"

        if len(alias) > 0:
            stmt += f" as {alias}"

        return stmt

    def parse_params_names_only(self) -> str:
        """
        Before| param1: int, param2: int = 42, param3=None
        After | param1, param2, param3
        """

        SEP: str = ", "

        params: List[str] = self.params_str.split(SEP)
        parsed_params: List[str] = []

        for param in params:
            colon_idx: int = param.find(":")

            # Type hint and beyond
            if colon_idx != -1:
                parsed_params.append(param[:colon_idx])
                continue

            # Kwargs and beyond
            equals_idx: int = param.find("=")
            if equals_idx != -1:
                parsed_params.append(param[:equals_idx])
                continue

        # Remove the last SEP
        parsed_params_str: str = SEP.join(parsed_params)
        return parsed_params_str

    def __hash__(self) -> int:
        return hash((self.module_name, self.function_name, self.params_str))
