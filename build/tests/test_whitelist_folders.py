"""
Unit tests for filtering Postman collection by whitelisted folders.
"""
import unittest
import os
import json
import tempfile
from unittest.mock import MagicMock
from postman_operations import read_whitelist_folders, filter_by_whitelist_folders


class TestWhitelistFolders(unittest.TestCase):
    """Test cases for filtering Postman collection by whitelisted folders."""

    def setUp(self):
        """Set up test fixtures."""
        self.logger = MagicMock()
        
        # Sample collection with different folders
        self.sample_collection = {
            "info": {
                "name": "Test Collection",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/"
            },
            "item": [
                {
                    "name": "Contacts",
                    "item": [
                        {
                            "name": "Get Contacts",
                            "request": {
                                "method": "GET",
                                "url": "https://example.com/contacts"
                            }
                        }
                    ]
                },
                {
                    "name": "Tasks",
                    "item": [
                        {
                            "name": "Get Tasks",
                            "request": {
                                "method": "GET",
                                "url": "https://example.com/tasks"
                            }
                        }
                    ]
                },
                {
                    "name": "Users",
                    "item": [
                        {
                            "name": "Get Users",
                            "request": {
                                "method": "GET",
                                "url": "https://example.com/users"
                            }
                        }
                    ]
                }
            ]
        }
        
        # Sample whitelist folders
        self.whitelist_folders = ["Contacts", "Tasks"]
        
        # Create a temporary whitelist file
        self.whitelist_file_content = {
            "folders": self.whitelist_folders
        }

    def test_read_whitelist_folders(self):
        """Test reading whitelist folders from a file."""
        # Create a temporary file with whitelist folders
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
            json.dump(self.whitelist_file_content, temp_file)
            temp_file_path = temp_file.name
        
        try:
            # Test reading the file
            result = read_whitelist_folders(temp_file_path, self.logger)
            self.assertEqual(result, self.whitelist_folders)
        finally:
            # Clean up the temporary file
            os.unlink(temp_file_path)
    
    def test_read_whitelist_folders_invalid_json(self):
        """Test reading whitelist folders from an invalid JSON file."""
        # Create a temporary file with invalid JSON
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
            temp_file.write("This is not valid JSON")
            temp_file_path = temp_file.name
        
        try:
            # Test reading the file
            with self.assertRaises(json.JSONDecodeError):
                read_whitelist_folders(temp_file_path, self.logger)
        finally:
            # Clean up the temporary file
            os.unlink(temp_file_path)
    
    def test_read_whitelist_folders_missing_key(self):
        """Test reading whitelist folders from a file missing the 'folders' key."""
        # Create a temporary file with missing 'folders' key
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
            json.dump({"not_folders": []}, temp_file)
            temp_file_path = temp_file.name
        
        try:
            # Test reading the file
            with self.assertRaises(KeyError):
                read_whitelist_folders(temp_file_path, self.logger)
        finally:
            # Clean up the temporary file
            os.unlink(temp_file_path)
    
    def test_filter_by_whitelist_folders(self):
        """Test filtering a collection by whitelisted folders."""
        result = filter_by_whitelist_folders(
            self.sample_collection, self.whitelist_folders, self.logger
        )
        
        # Check that only whitelisted folders are included
        self.assertEqual(len(result["item"]), 2)
        self.assertEqual(result["item"][0]["name"], "Contacts")
        self.assertEqual(result["item"][1]["name"], "Tasks")
    
    def test_filter_by_whitelist_folders_no_matches(self):
        """Test filtering when no folders match the whitelist."""
        result = filter_by_whitelist_folders(
            self.sample_collection, ["NonexistentFolder"], self.logger
        )
        
        # Check that no folders are included
        self.assertEqual(len(result["item"]), 0)
    
    def test_filter_by_whitelist_folders_empty_whitelist(self):
        """Test filtering with an empty whitelist."""
        result = filter_by_whitelist_folders(
            self.sample_collection, [], self.logger
        )
        
        # Check that no folders are included
        self.assertEqual(len(result["item"]), 0)
    
    def test_filter_by_whitelist_folders_non_dict_input(self):
        """Test filtering with a non-dictionary input."""
        result = filter_by_whitelist_folders(
            "not a dict", self.whitelist_folders, self.logger
        )
        
        # Check that the input is returned unchanged
        self.assertEqual(result, "not a dict")


if __name__ == '__main__':
    unittest.main()