# Postman Collection Subset Generator

This application generates a subset of a Postman Collection. It can filter the collection by endpoint type and optionally remove description fields.

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
