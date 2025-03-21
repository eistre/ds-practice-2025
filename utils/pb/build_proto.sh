#!/bin/bash

# List all directories in the current directory
for dir in */; do
    # Remove trailing slash from directory name
    dir=${dir%/}

    # Check if the directory contains a .proto file
    if [ -f $dir/*.proto ]; then
        # Move into the directory
        cd $dir

        # Echo out the directory name
        echo "Building proto file in $dir"

        # Generate the python code from the .proto file
        python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. $dir.proto

        # Move back to the original directory
        cd ..
    fi
done
