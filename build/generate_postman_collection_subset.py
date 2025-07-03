#!/usr/bin/env python3
"""
Entry point for the console application.
"""
import sys
import os
import json
import logging
import argparse
from postman_operations import (remove_descriptions, filter_by_endpoint_type,
                               read_whitelist_folders, filter_by_whitelist_folders)


def setup_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    return logging.getLogger(__name__)


def parse_arguments(args=None):
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed command line arguments
    """
    parser = argparse.ArgumentParser(
        description='Generate a subset of a Postman Collection.'
    )
    parser.add_argument(
        '--input-file',
        required=True,
        help='Path to the input Postman Collection JSON file'
    )
    parser.add_argument(
        '--output-file',
        required=True,
        help='Path to save the output Postman Subset JSON file'
    )
    parser.add_argument(
        '--remove-descriptions',
        action='store_true',
        help='Remove all description fields from the Postman Collection')
    parser.add_argument(
        '--only-endpoints-type',
        type=str,
        choices=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        help='Include only endpoints of the specified type'
    )
    parser.add_argument(
        '--whitelist-folders',
        type=str,
        help='Path to a JSON file containing folder names to include'
    )
    return parser.parse_args(args)


def read_postman_collection(file_path, logger):
    """
    Read a Postman Collection from a JSON file.
    
    Args:
        file_path (str): Path to the Postman Collection JSON file
        logger (logging.Logger): Logger instance
        
    Returns:
        dict: The Postman Collection as a Python dictionary
        
    Raises:
        FileNotFoundError: If the input file does not exist
        json.JSONDecodeError: If the input file is not valid JSON
    """
    logger.info(f"Reading Postman Collection from {file_path}")
    if not os.path.exists(file_path):
        logger.error(f"Input file not found: {file_path}")
        raise FileNotFoundError(f"Input file not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            return json.load(file)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from {file_path}: {e}")
            raise


def write_postman_subset(collection, file_path, logger):
    """
    Write a Postman Subset to a JSON file.
    
    Args:
        collection (dict): The Postman Collection/Subset as a Python dictionary
        file_path (str): Path to save the Postman Subset JSON file
        logger (logging.Logger): Logger instance
    """
    logger.info(f"Writing Postman Subset to {file_path}")
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(collection, file, indent=2)


def main():
    """
    Main entry point for the application.
    
    Returns:
        int: Exit code (0 for success, non-zero for errors)
    """
    try:
        logger = setup_logging()
        logger.debug("Application started")
        
        # Parse command line arguments
        args = parse_arguments()
        
        # Read the input Postman Collection
        collection = read_postman_collection(args.input_file, logger)
        
        # Filter by whitelist folders if requested
        if args.whitelist_folders:
            logger.info(f"Filtering collection to include only whitelisted folders")
            whitelist_folders = read_whitelist_folders(args.whitelist_folders, logger)
            collection = filter_by_whitelist_folders(collection, whitelist_folders, logger)
            if not collection.get('item'):
                logger.warning("No whitelisted folders found in the collection")
        
        # Filter by endpoint type if requested
        if args.only_endpoints_type:
            logger.info(f"Filtering collection to include only {args.only_endpoints_type} endpoints")
            collection = filter_by_endpoint_type(collection, args.only_endpoints_type, logger)
            if not collection:
                logger.warning(f"No {args.only_endpoints_type} endpoints found in the collection")
        
        # Remove descriptions if requested
        if args.remove_descriptions:
            logger.info("Removing description fields from the Postman Collection")
            collection = remove_descriptions(collection, logger)
        
        # For now, the subset is the same as the full collection
        # In the future, this is where filtering logic would be added
        
        # Write the Postman Subset to the output file
        write_postman_subset(collection, args.output_file, logger)
        
        logger.debug("Application completed successfully")
        return 0
    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
        return 2
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON: {e}")
        return 3
    except KeyError as e:
        return 3
    except Exception as e:
        # If logger is not defined (e.g., setup_logging failed), use root logger
        try:
            logger.error(f"An error occurred: {e}", exc_info=True)
        except UnboundLocalError:
            # Fallback to root logger if logger is not defined
            logging.error(f"An error occurred during application startup: {e}", exc_info=True)
        
        return 1


if __name__ == "__main__":
    sys.exit(main())