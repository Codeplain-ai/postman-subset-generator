# Postman Collection Subset Generator

## System Requirements

- Python 3.10 or higher

## Requirements

No external dependencies are required. The application uses only Python standard library modules.

## Installation

No installation is required. Simply clone the repository and run the script.

## Usage

```bash
python generate_postman_collection_subset.py --input-file <input_file> --output-file <output_file>
```

Where:
- `<input_file>` is the path to the input Postman Collection JSON file
- `<output_file>` is the path to save the output Postman Subset JSON file

## Full usage

```
❯ python3 generate_postman_collection_subset.py --help
usage: generate_postman_collection_subset.py [-h] --input-file INPUT_FILE --output-file OUTPUT_FILE [--remove-descriptions] [--only-endpoints-type {GET,POST,PUT,DELETE,PATCH,OPTIONS}] [--whitelist-folders WHITELIST_FOLDERS]

Generate a subset of a Postman Collection.

options:
  -h, --help            show this help message and exit
  --input-file INPUT_FILE
                        Path to the input Postman Collection JSON file
  --output-file OUTPUT_FILE
                        Path to save the output Postman Subset JSON file
  --remove-descriptions
                        Remove all description fields from the Postman Collection
  --only-endpoints-type {GET,POST,PUT,DELETE,PATCH,OPTIONS}
                        Include only endpoints of the specified type
  --whitelist-folders WHITELIST_FOLDERS
                        Path to a JSON file containing folder names to include
```