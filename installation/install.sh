#!/usr/bin/env bash

echo "This is a bash script"
cat << EOF | python3 -
import sys
print(f"Python version: {sys.version}")
EOF

