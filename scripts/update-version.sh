# Run this after updating the pyproject.toml
# This script is meant to be run from the root of the repo as `scripts/update-version.sh`

version=$(python3 scripts/helpers/read-version.py)

# First, the pre-hooks
python3 ./prebuild.py

# Then, the other stuff
pixi install
pixi install -e dev

git status
git add .

git commit -m "[UPDATE] v$version"

# Must happen after or else will point to a previous commit
git tag "v$version"

git push origin main "v$version"
