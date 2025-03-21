#!/bin/bash

# List all directories in the current directory
for dir in */; do
    # Remove trailing slash from directory name
    dir=${dir%/}

    # Check if the directory contains a .proto file
    if [ -f $dir/*.proto ]; then

        # Echo out the directory name
        echo "Building proto file in $dir"

        # Generate the python code from the .proto file
        python -m grpc_tools.protoc --proto_path=. --python_out=. --pyi_out=. --grpc_python_out=. $dir/*.proto

    fi
done
