#!/bin/bash

# Check if subfolder name is provided
if [ -z "$1" ]; then
  echo "Error: No subfolder name provided."
  echo "Usage: $0 <subfolder_name>"
  exit 1
fi

# Move to the subfolder
cd "$1" 2>/dev/null

# Check if the subfolder exists
if [ $? -ne 0 ]; then
  echo "Error: Subfolder '$1' does not exist."
  exit 2
fi

# Create and activate virtual environment
python3.12 -m venv .venv
source .venv/bin/activate

# Install requirements if requirements.txt exists
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt >/dev/null 2>&1
else
    echo "Error: requirements.txt not found. Cannot proceed with setup."
    deactivate
    rm -rf .venv
    exit 4
fi

# Execute all Python unittests in the subfolder
echo "Running Python unittests in $1..."

output=$(timeout 60s python -m unittest discover -b 2>&1)
exit_code=$?

# Check if the command timed out
if [ $exit_code -eq 124 ]; then
    printf "\nError: Unittests timed out after 60 seconds.\n"
    exit 3
fi

# Echo the original output
echo "$output"

# Deactivate and remove virtual environment
deactivate
rm -rf .venv

# Return the exit code of the unittest command
exit $exit_code

# Note: The 'discover' option automatically identifies and runs all unittests in the current directory and subdirectories
# Ensure that your Python files are named according to the unittest discovery pattern (test*.py by default)
