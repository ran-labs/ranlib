import inspect
import functools


module_name = inspect.getmodule(inspect.currentframe()).__name__

print(module_name)


def fn():
    print("called function")
