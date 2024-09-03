#!/usr/bin/env bash

a="Hello"
b=2
declare c="reseljlfjk"
declare k='NowThen'

echo "This is a bash script $a $b $c"
cat << EOF | python3 -
import sys
print(f"Python version: {sys.version}")
EOF

