import sys
import yaml


def modify_recipe(recipe_path: str):
    # Read it
    with open(recipe_path, 'r') as recipe_file:
        recipe: dict = yaml.safe_load(recipe_file)
    
    # Modify it

    # For whatever reason, rattler-build does not copy in the LICENSE so we have to take it manually
    # TODO: once the repo is public, use our own repo's LICENSE file for a free automation
    # For now, just use the one in this link
    LICENSE_URL: str = "https://raw.githubusercontent.com/AmeerArsala/apache-license/refs/heads/main/LICENSE"
    curl_cmd: str = f"curl {LICENSE_URL} -o ./LICENSE"

    # Python install command
    py_install_cmd: str = "${{ PYTHON }} -m pip install ./${{ name|lower }}-${{ version }}.tar.gz -vv --no-deps --no-build-isolation"
    
    # modify file
    recipe["build"]["script"] = f"{curl_cmd} && {py_install_cmd}"
    #recipe["build"]["script"] = py_install_cmd
    
    # Write it
    with open(recipe_path, 'w') as recipe_file:
        yaml.dump(recipe, recipe_file)
    
    print("Recipe modified.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        recipe_path: str = sys.argv[1]
        modify_recipe(recipe_path)
    else:
        print("Usage: recipe-preprocessor.py <recipe.yaml path>")
        sys.exit(1)
