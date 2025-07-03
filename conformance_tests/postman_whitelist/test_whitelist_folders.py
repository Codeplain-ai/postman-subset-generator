#!/usr/bin/env python3
"""
Conformance tests for the whitelist folders functionality of the Postman Collection Subset Generator.
"""
import unittest
import os
import json
import tempfile
import subprocess
import shutil


class TestWhitelistFolders(unittest.TestCase):
    """Test cases for the --whitelist-folders functionality."""

    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        
        # Create the example Postman collection content
        self.example_collection = {
            "info": {
                "_postman_id": "c39a5e25-dad6-4a1c-a481-a83d83216810",
                "name": "Wrike selected endpoints",
                "description": "Use the collection as a reference to the official [API documentation](https://developers.wrike.com/)documentation/\n\nOnce imported you should create an environment with two variables.\n\nAPIToken containing your Wrike API Token  \nWrikeAPI containing the API URL Base like\n\n- [https://www.wrike.com/api/v4](https://www.wrike.com/api/v4)\n    \n- [https://eu-app.wrike.com/api/v4](https://eu-app.wrike.com/api/v4)",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
                "_exporter_id": "41935379"
            },
            "item": [
                {
                    "name": "Comments",
                    "item": [
                        {
                            "name": "Get Comments",
                            "request": {
                                "method": "GET",
                                "header": [],
                                "url": {
                                    "raw": "{{WrikeAPI}}/comments",
                                    "host": [
                                        "{{WrikeAPI}}"
                                    ],
                                    "path": [
                                        "comments"
                                    ]
                                },
                                "description": "Get all comments on all items shared with you\n\nhttps://developers.wrike.com/api/v4/comments/#get-comments"
                            },
                            "response": []
                        }
                    ]
                },
                {
                    "name": "Attachments",
                    "item": [
                        {
                            "name": "Get Attachments",
                            "request": {
                                "method": "GET",
                                "header": [],
                                "url": {
                                    "raw": "{{WrikeAPI}}/attachments?versions=true&createdDate={\"start\":\"2020-07-01T00:00:00Z\",\"end\":\"2020-07-02T07:53:33Z\"}&withUrls=true",
                                    "host": [
                                        "{{WrikeAPI}}"
                                    ],
                                    "path": [
                                        "attachments"
                                    ],
                                    "query": [
                                        {
                                            "key": "versions",
                                            "value": "true",
                                            "description": "Optional"
                                        },
                                        {
                                            "key": "createdDate",
                                            "value": "{\"start\":\"2020-07-01T00:00:00Z\",\"end\":\"2020-07-02T07:53:33Z\"}",
                                            "description": "Optional"
                                        },
                                        {
                                            "key": "withUrls",
                                            "value": "true",
                                            "description": "Optional"
                                        }
                                    ]
                                },
                                "description": "Get all attachments\n\nhttps://developers.wrike.com/api/v4/attachments/#get-attachments"
                            },
                            "response": []
                        },
                        {
                            "name": "Create Wrike Attachment on Task",
                            "request": {
                                "method": "POST",
                                "header": [],
                                "url": {
                                    "raw": "{{WrikeAPI}}/tasks/IEACW7SVKQPX4WGU/attachments",
                                    "host": [
                                        "{{WrikeAPI}}"
                                    ],
                                    "path": [
                                        "tasks",
                                        "IEACW7SVKQPX4WGU",
                                        "attachments"
                                    ]
                                },
                                "description": "Create a new attachment on a Wrike task\n\nhttps://developers.wrike.com/api/v4/attachments/#create-wrike-attachment"
                            },
                            "response": []
                        }
                    ]
                }
            ],
            "auth": {
                "type": "bearer",
                "bearer": [
                    {
                        "key": "token",
                        "value": "{{APIToken}}",
                        "type": "string"
                    }
                ]
            },
            "event": [
                {
                    "listen": "prerequest",
                    "script": {
                        "type": "text/javascript",
                        "exec": [
                            ""
                        ]
                    }
                },
                {
                    "listen": "test",
                    "script": {
                        "type": "text/javascript",
                        "exec": [
                            ""
                        ]
                    }
                }
            ]
        }
        
        # Path to the example Postman collection
        self.example_collection_path = os.path.join(self.test_dir, "example_collection.json")
        
        # Write the example collection to a file
        with open(self.example_collection_path, "w", encoding="utf-8") as out_f:
            json.dump(self.example_collection, out_f)
        
        # Path for output file
        self.output_path = os.path.join(self.test_dir, "output.json")

    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary directory and its contents
        shutil.rmtree(self.test_dir)

    def create_whitelist_file(self, folders):
        """Create a whitelist file with the given folders.
        
        Args:
            folders (list): List of folder names to include in the whitelist
            
        Returns:
            str: Path to the created whitelist file
        """
        whitelist_path = os.path.join(self.test_dir, "whitelist.json")
        with open(whitelist_path, "w", encoding="utf-8") as f:
            json.dump({"folders": folders}, f)
        return whitelist_path

    def run_app(self, whitelist_path=None):
        """Run the application with the given whitelist file.
        
        Args:
            whitelist_path (str, optional): Path to the whitelist file
            
        Returns:
            int: Return code from the application
        """
        cmd = [
            "python", 
            "generate_postman_collection_subset.py",
            "--input-file", self.example_collection_path,
            "--output-file", self.output_path
        ]
        
        if whitelist_path:
            cmd.extend(["--whitelist-folders", whitelist_path])
        
        process = subprocess.run(cmd, capture_output=True, text=True)
        return process

    def test_basic_whitelist_functionality(self):
        """Test that only whitelisted folders are included in the output."""
        # Create whitelist with only "Attachments" folder
        whitelist_path = self.create_whitelist_file(["Attachments"])
        
        # Run the application
        process = self.run_app(whitelist_path)
        
        # Check that the application ran successfully
        self.assertEqual(process.returncode, 0, 
                         f"Application failed with error: {process.stderr}")
        
        # Check that the output file exists
        self.assertTrue(os.path.exists(self.output_path), 
                        "Output file was not created")
        
        # Load the output file
        with open(self.output_path, "r", encoding="utf-8") as f:
            output = json.load(f)
        
        # Check that only the whitelisted folder is included
        self.assertEqual(len(output["item"]), 1, 
                         f"Expected 1 folder, got {len(output['item'])}")
        self.assertEqual(output["item"][0]["name"], "Attachments", 
                         f"Expected 'Attachments' folder, got '{output['item'][0]['name']}'")

    def test_multiple_whitelisted_folders(self):
        """Test that multiple whitelisted folders are included in the output."""
        # Create whitelist with both folders from the example collection
        whitelist_path = self.create_whitelist_file(["Comments", "Attachments"])
        
        # Run the application
        process = self.run_app(whitelist_path)
        
        # Check that the application ran successfully
        self.assertEqual(process.returncode, 0, 
                         f"Application failed with error: {process.stderr}")
        
        # Load the output file
        with open(self.output_path, "r", encoding="utf-8") as f:
            output = json.load(f)
        
        # Check that both whitelisted folders are included
        self.assertEqual(len(output["item"]), 2, 
                         f"Expected 2 folders, got {len(output['item'])}")
        
        # Check folder names (order may vary)
        folder_names = [item["name"] for item in output["item"]]
        self.assertIn("Comments", folder_names, 
                      f"Expected 'Comments' folder, got {folder_names}")
        self.assertIn("Attachments", folder_names, 
                      f"Expected 'Attachments' folder, got {folder_names}")

    def test_empty_whitelist(self):
        """Test behavior when the whitelist contains no folders."""
        # Create empty whitelist
        whitelist_path = self.create_whitelist_file([])
        
        # Run the application
        process = self.run_app(whitelist_path)
        
        # Check that the application ran successfully
        self.assertEqual(process.returncode, 0, 
                         f"Application failed with error: {process.stderr}")
        
        # Load the output file
        with open(self.output_path, "r", encoding="utf-8") as f:
            output = json.load(f)
        
        # Check that no folders are included
        self.assertEqual(len(output["item"]), 0, 
                         f"Expected 0 folders, got {len(output['item'])}")

    def test_nonexistent_folder(self):
        """Test behavior when the whitelist contains folders that don't exist in the collection."""
        # Create whitelist with a non-existent folder
        whitelist_path = self.create_whitelist_file(["NonExistentFolder"])
        
        # Run the application
        process = self.run_app(whitelist_path)
        
        # Check that the application ran successfully
        self.assertEqual(process.returncode, 0, 
                         f"Application failed with error: {process.stderr}")
        
        # Load the output file
        with open(self.output_path, "r", encoding="utf-8") as f:
            output = json.load(f)
        
        # Check that no folders are included
        self.assertEqual(len(output["item"]), 0, 
                         f"Expected 0 folders, got {len(output['item'])}")

    def test_case_sensitivity(self):
        """Test that folder name matching is case-sensitive."""
        # Create whitelist with case variations of folder names
        whitelist_path = self.create_whitelist_file(["attachments", "COMMENTS"])
        
        # Run the application
        process = self.run_app(whitelist_path)
        
        # Check that the application ran successfully
        self.assertEqual(process.returncode, 0, 
                         f"Application failed with error: {process.stderr}")
        
        # Load the output file
        with open(self.output_path, "r", encoding="utf-8") as f:
            output = json.load(f)
        
        # Check that no folders are included (since case doesn't match)
        self.assertEqual(len(output["item"]), 0, 
                         f"Expected 0 folders, got {len(output['item'])}")

    def test_invalid_whitelist_file(self):
        """Test behavior when the whitelist file is invalid JSON."""
        # Create an invalid whitelist file
        whitelist_path = os.path.join(self.test_dir, "invalid_whitelist.json")
        with open(whitelist_path, "w", encoding="utf-8") as f:
            f.write("This is not valid JSON")
        
        # Run the application
        process = self.run_app(whitelist_path)
        
        # Check that the application failed
        self.assertNotEqual(process.returncode, 0, 
                            "Application should have failed with invalid whitelist file")

    def test_missing_whitelist_file(self):
        """Test behavior when the whitelist file doesn't exist."""
        # Path to a non-existent whitelist file
        whitelist_path = os.path.join(self.test_dir, "nonexistent_whitelist.json")
        
        # Run the application
        process = self.run_app(whitelist_path)
        
        # Check that the application failed
        self.assertNotEqual(process.returncode, 0, 
                            "Application should have failed with missing whitelist file")


if __name__ == "__main__":
    unittest.main()