#!/bin/bash
# ----------------------------------------------------------
# Script: lowercase_files.sh
# Author: Evangelos Papadopoulos
# Date: 2025-09-22
# Version: 1.1
#
# Function:
#   Converts all filenames in a given folder to lowercase.
#   Supports a dry-run option to preview changes without renaming.
#
# Usage:
#   ./lowercase_files.sh <folder> [--dry-run]
#
# Example:
#   ./lowercase_files.sh /path/to/myfiles
#   ./lowercase_files.sh /path/to/myfiles --dry-run
# ----------------------------------------------------------

# If no arguments provided, print usage and exit
if [ $# -lt 1 ]; then
    echo "----------------------------------------------------------"
    echo "Version: 1.1"
    echo "Function:"
    echo "  Converts all filenames in a given folder to lowercase."
    echo "Usage:"
    echo "  $0 <folder> [--dry-run]"
    echo "Example:"
    echo "  $0 /path/to/myfiles"
    echo "  $0 /path/to/myfiles --dry-run"
    echo "----------------------------------------------------------"
    exit 1
fi

TARGET_DIR=$1
DRY_RUN=false

if [ "$2" == "--dry-run" ]; then
    DRY_RUN=true
fi

# Check if argument is a directory
if [ ! -d "$TARGET_DIR" ]; then
    echo "Error: $TARGET_DIR is not a valid directory."
    exit 2
fi

# Loop through all files and rename to lowercase
for f in "$TARGET_DIR"/*; do
    if [ -f "$f" ]; then
        new_name="$(basename "$f" | tr '[:upper:]' '[:lower:]')"
        dir_name="$(dirname "$f")"
        if [ "$f" != "$dir_name/$new_name" ]; then
            echo "Renaming: $f -> $dir_name/$new_name"
            if [ "$DRY_RUN" = false ]; then
                mv "$f" "$dir_name/$new_name"
            fi
        fi
    fi
done

