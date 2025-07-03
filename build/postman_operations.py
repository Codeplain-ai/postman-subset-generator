#!/usr/bin/env python3
"""
Operations for manipulating Postman collections.
"""
import logging
import json


def remove_descriptions(data, logger):
    """
    Recursively remove all 'description' fields from the Postman Collection.
    
    Args:
        data: The data structure to process (dict, list, or other value)
        logger (logging.Logger): Logger instance
        
    Returns:
        The data structure with all 'description' fields removed
    """
    if isinstance(data, dict):
        # Create a new dict to avoid modifying the original during iteration
        result = {}
        for key, value in data.items():
            if key == 'description':
                logger.debug("Removing description field")
                continue  # Skip this key-value pair
            result[key] = remove_descriptions(value, logger)
        return result
    elif isinstance(data, list):
        return [remove_descriptions(item, logger) for item in data]
    else:
        # For primitive values, just return them unchanged
        return data


def filter_by_endpoint_type(data, endpoint_type, logger):
    """
    Recursively filter the Postman Collection to include only endpoints of the specified type.
    
    Args:
        data: The data structure to process (dict, list, or other value)
        endpoint_type (str): The endpoint type to filter by (e.g., "GET", "POST")
        logger (logging.Logger): Logger instance
        
    Returns:
        The filtered data structure
    """
    if isinstance(data, dict):
        # Check if this is a request item with a method
        if 'request' in data and isinstance(data['request'], dict) and 'method' in data['request']:
            # If the method doesn't match, return None to exclude this item
            if data['request']['method'] != endpoint_type:
                logger.debug(f"Excluding request with method {data['request']['method']}")
                return None
            logger.debug(f"Including request with method {data['request']['method']}")
        
        # Process all key-value pairs in the dictionary
        result = {}
        for key, value in data.items():
            filtered_value = filter_by_endpoint_type(value, endpoint_type, logger)
            # Only include non-None values
            if filtered_value is not None:
                result[key] = filtered_value
        
        # If this is an item array and it's now empty, return None
        if 'item' in data and not result.get('item', []):
            return None
        
        return result
    elif isinstance(data, list):
        # Filter the list items, removing None values
        filtered_list = [
            filtered_item for item in data
            if (filtered_item := filter_by_endpoint_type(item, endpoint_type, logger)) is not None
        ]
        # If the list is now empty, return None
        return filtered_list if filtered_list else None
    else:
        # For primitive values, just return them unchanged
        return data


def read_whitelist_folders(file_path, logger):
    """
    Read the whitelist folders from a JSON file.
    
    Args:
        file_path (str): Path to the whitelist folders JSON file
        logger (logging.Logger): Logger instance
        
    Returns:
        list: List of folder names to include
        
    Raises:
        FileNotFoundError: If the whitelist file does not exist
        json.JSONDecodeError: If the whitelist file is not valid JSON
        KeyError: If the whitelist file does not contain the 'folders' key
    """
    logger.info(f"Reading whitelist folders from {file_path}")
    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            data = json.load(file)
            if 'folders' not in data:
                logger.error("Whitelist file does not contain 'folders' key")
                raise KeyError("Whitelist file must contain a 'folders' key with an array of folder names")
            return data['folders']
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from {file_path}: {e}")
            raise


def filter_by_whitelist_folders(data, whitelist_folders, logger):
    """
    Filter the Postman Collection to include only whitelisted folders.
    
    Args:
        data (dict): The Postman Collection
        whitelist_folders (list): List of folder names to include
        logger (logging.Logger): Logger instance
        
    Returns:
        dict: The filtered Postman Collection
    """
    if not isinstance(data, dict) or 'item' not in data:
        return data
    
    # Filter the top-level items to include only whitelisted folders
    data['item'] = [item for item in data['item'] if item.get('name') in whitelist_folders]
    logger.info(f"Filtered collection to include only {len(data['item'])} whitelisted folders")
    
    return data