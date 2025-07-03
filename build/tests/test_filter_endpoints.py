"""
Unit tests for filtering Postman collection by endpoint type.
"""
import unittest
from unittest.mock import MagicMock
from postman_operations import filter_by_endpoint_type


class TestFilterEndpoints(unittest.TestCase):
    """Test cases for filtering Postman collection by endpoint type."""

    def setUp(self):
        """Set up test fixtures."""
        self.logger = MagicMock()
        
        # Sample collection with different endpoint types
        self.sample_collection = {
            "info": {
                "name": "Test Collection",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/"
            },
            "item": [
                {
                    "name": "GET Request",
                    "request": {
                        "method": "GET",
                        "url": "https://example.com/get"
                    }
                },
                {
                    "name": "POST Request",
                    "request": {
                        "method": "POST",
                        "url": "https://example.com/post"
                    }
                },
                {
                    "name": "Folder",
                    "item": [
                        {
                            "name": "PUT Request",
                            "request": {
                                "method": "PUT",
                                "url": "https://example.com/put"
                            }
                        },
                        {
                            "name": "DELETE Request",
                            "request": {
                                "method": "DELETE",
                                "url": "https://example.com/delete"
                            }
                        }
                    ]
                }
            ]
        }

    def test_filter_by_get(self):
        """Test filtering to include only GET endpoints."""
        result = filter_by_endpoint_type(
            self.sample_collection, "GET", self.logger
        )
        
        # Check that only GET requests are included
        self.assertEqual(len(result["item"]), 1)
        self.assertEqual(result["item"][0]["name"], "GET Request")
        self.assertEqual(result["item"][0]["request"]["method"], "GET")

    def test_filter_by_post(self):
        """Test filtering to include only POST endpoints."""
        result = filter_by_endpoint_type(
            self.sample_collection, "POST", self.logger
        )
        
        # Check that only POST requests are included
        self.assertEqual(len(result["item"]), 1)
        self.assertEqual(result["item"][0]["name"], "POST Request")
        self.assertEqual(result["item"][0]["request"]["method"], "POST")

    def test_filter_nested_folders(self):
        """Test filtering with nested folders."""
        result = filter_by_endpoint_type(
            self.sample_collection, "PUT", self.logger
        )
        
        # Check that the folder structure is preserved
        self.assertEqual(len(result["item"]), 1)
        self.assertEqual(result["item"][0]["name"], "Folder")
        self.assertEqual(len(result["item"][0]["item"]), 1)
        self.assertEqual(result["item"][0]["item"][0]["name"], "PUT Request")
        self.assertEqual(result["item"][0]["item"][0]["request"]["method"], "PUT")

    def test_filter_no_matches(self):
        """Test filtering when no endpoints match the specified type."""
        result = filter_by_endpoint_type(
            self.sample_collection, "OPTIONS", self.logger
        )
        
        # Check that the result is None when no matches are found
        self.assertIsNone(result)

    def test_filter_empty_collection(self):
        """Test filtering an empty collection."""
        empty_collection = {
            "info": {
                "name": "Empty Collection",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/"
            },
            "item": []
        }
        
        result = filter_by_endpoint_type(
            empty_collection, "GET", self.logger
        )
        
        # Check that the result is None for an empty collection
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()