"""
Test helpers and fixtures for Postman Collection Subset Generator tests.
"""
import json
import tempfile
import os
from unittest.mock import MagicMock


# Sample Postman Collection data for testing
SAMPLE_COLLECTION = {
    "info": {
        "name": "Sample Collection",
        "description": "This is a sample collection for testing",
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/"
    },
    "item": [
        {
            "name": "Sample Request",
            "description": "This is a sample request",
            "request": {
                "url": "https://example.com",
                "method": "GET",
                "description": "Request description"
            }
        }
    ]
}

# Sample collection without descriptions
SAMPLE_COLLECTION_NO_DESC = {
    "info": {
        "name": "Sample Collection",
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/"
    },
    "item": [
        {
            "name": "Sample Request",
            "request": {
                "url": "https://example.com",
                "method": "GET"
            }
        }
    ]
}


def create_temp_json_file(data):
    """
    Create a temporary file with JSON data.
    
    Args:
        data (dict): The data to write to the file
        
    Returns:
        str: The path to the temporary file
    """
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
        json.dump(data, temp_file)
        return temp_file.name


def create_mock_args(input_file='input.json', output_file='output.json', remove_descriptions=False, only_endpoints_type=None, whitelist_folders=None):
    """
    Create a mock arguments object for testing.
    
    Args:
        input_file (str): The input file path
        output_file (str): The output file path
        remove_descriptions (bool): Whether to remove descriptions
        only_endpoints_type (str): The endpoint type to filter by
        whitelist_folders (str): Path to the whitelist folders file
        
    Returns:
        MagicMock: A mock arguments object
    """
    mock_args = MagicMock()
    mock_args.input_file = input_file
    mock_args.output_file = output_file
    mock_args.remove_descriptions = remove_descriptions
    mock_args.only_endpoints_type = only_endpoints_type
    mock_args.whitelist_folders = whitelist_folders
    return mock_args