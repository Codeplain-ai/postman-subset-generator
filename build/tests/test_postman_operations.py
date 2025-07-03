"""
Unit tests for Postman collection operations.
"""
import unittest
import os
import json
import tempfile
from unittest.mock import MagicMock
from postman_operations import remove_descriptions
import generate_postman_collection_subset
from tests.test_helpers import (
    SAMPLE_COLLECTION,
    create_temp_json_file
)


class TestPostmanOperations(unittest.TestCase):
    """Test cases for Postman collection operations."""

    def test_read_postman_collection(self):
        """Test reading a Postman Collection from a file."""
        # Create a temporary file with sample collection
        temp_file_path = create_temp_json_file(SAMPLE_COLLECTION)

        try:
            # Test reading the file
            logger = MagicMock()
            result = generate_postman_collection_subset.read_postman_collection(temp_file_path, logger)
            self.assertEqual(result, SAMPLE_COLLECTION)
        finally:
            # Clean up the temporary file
            os.unlink(temp_file_path)

    def test_write_postman_subset(self):
        """Test writing a Postman Subset to a file."""
        # Create a temporary file for output
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name

        try:
            # Test writing to the file
            logger = MagicMock()
            generate_postman_collection_subset.write_postman_subset(SAMPLE_COLLECTION, temp_file_path, logger)
            
            # Verify the file was written correctly
            with open(temp_file_path, 'r') as file:
                result = json.load(file)
                self.assertEqual(result, SAMPLE_COLLECTION)
        finally:
            # Clean up the temporary file
            os.unlink(temp_file_path)

    def test_remove_descriptions(self):
        """Test removing description fields from a collection."""
        logger = MagicMock()
        
        # Test with a collection that has description fields
        result = remove_descriptions(SAMPLE_COLLECTION, logger)
        
        # Verify that all description fields are removed
        self.assertNotIn('description', result['info'])
        self.assertNotIn('description', result['item'][0])
        self.assertNotIn('description', result['item'][0]['request'])
        
        # Test with a nested structure
        nested_data = {
            'level1': {
                'description': 'Level 1 description',
                'level2': {
                    'description': 'Level 2 description',
                    'data': 'value'
                }
            }
        }
        result = remove_descriptions(nested_data, logger)
        self.assertNotIn('description', result['level1'])
        self.assertNotIn('description', result['level1']['level2'])
        self.assertEqual(result['level1']['level2']['data'], 'value')


if __name__ == '__main__':
    unittest.main()