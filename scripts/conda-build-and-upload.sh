#!/usr/bin/env bash

# NOTE: This should be executed as `scripts/conda-build-and-upload.sh`, not `./conda-build-and-upload.sh`
# Additionally, this file assumes you already have the prerequisites installed
# Assumes grayskull = 2.7.2, rattler-build = 0.22.0

# Find the built PyPI package
pypi_build=$(find ./dist -maxdepth 1 -type f -name "*.tar.gz" | head -n 1)

# make temp directory
mkdir temp

# Generate a meta.yaml from the local pypi build that already happened
grayskull pypi "$pypi_build" --output ./temp

recipe="temp/recipe.yaml"

# Convert meta.yaml to a recipe.yaml
conda-recipe-manager convert temp/ranlib/meta.yaml > $recipe

# Now, modify the recipe.yaml
python3 scripts/helpers/recipe-preprocessor.py "$recipe"

# Build it for conda with rattler-build
rattler-build build --recipe $recipe

# remove temp directory
rm -rf temp

# Get the .conda file to upload
conda_build=$(find ./output/noarch -maxdepth 1 -type f -name "*.conda" | head -n 1)
#echo "LOCATION: $conda_build"

# Upload to prefix.dev
pixi run -e dev python3 scripts/upload-prefixdev.py "$conda_build" "$PREFIX_DEV_TOKEN"
