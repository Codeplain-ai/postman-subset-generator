#!/usr/bin/env python3
"""
Acceptance test for the whitelist folders functionality of the Postman Collection Subset Generator.
"""
import unittest
import os
import json
import tempfile
import subprocess
import shutil


class TestAcceptanceWhitelistFolders(unittest.TestCase):
    """Acceptance test for the --whitelist-folders functionality."""

    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        # Get the directory where the test file is located
        self.test_file_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Create paths for resource files
        self.example_collection_path = os.path.join(self.test_dir, "wrike_postman_example.json")
        self.whitelist_folders_path = os.path.join(self.test_dir, "whitelisted-folders.json")
        self.expected_output_path = os.path.join(self.test_dir, "wrike_postman_example_condensed.json")
        self.output_path = os.path.join(self.test_dir, "output.json")
        self.resource_dir = self.test_file_dir
        
        # Load and save the example Postman collection
        with open(os.path.join(self.resource_dir, "wrike_postman_example.json"), "r", encoding="utf-8") as f:
            example_collection = json.load(f)
        with open(self.example_collection_path, "w", encoding="utf-8") as f:
            json.dump(example_collection, f)
        
        # Load and save the whitelist folders
        with open(os.path.join(self.resource_dir, "whitelisted-folders.json"), "r", encoding="utf-8") as f:
            whitelist_folders = json.load(f)
        with open(self.whitelist_folders_path, "w", encoding="utf-8") as f:
            json.dump(whitelist_folders, f)
        
        # Load and save the expected condensed output
        with open(os.path.join(self.resource_dir, "wrike_postman_example_condensed.json"), "r", encoding="utf-8") as f:
            expected_output = json.load(f)
        with open(self.expected_output_path, "w", encoding="utf-8") as f:
            json.dump(expected_output, f)

    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary directory and its contents
        shutil.rmtree(self.test_dir)

    def test_whitelist_folders_acceptance(self):
        """
        Test that using --whitelist-folders with whitelisted-folders.json on wrike_postman_example.json
        produces output matching wrike_postman_example_condensed.json.
        """
        # Run the application with whitelist folders
        cmd = [
            "python", 
            "generate_postman_collection_subset.py",
            "--input-file", self.example_collection_path,
            "--output-file", self.output_path,
            "--whitelist-folders", self.whitelist_folders_path
        ]
        
        process = subprocess.run(cmd, capture_output=True, text=True)
        
        # Check that the application ran successfully
        self.assertEqual(process.returncode, 0, 
                         f"Application failed with error: {process.stderr}")
        
        # Check that the output file exists
        self.assertTrue(os.path.exists(self.output_path), 
                        "Output file was not created")
        
        # Load the output file
        with open(self.output_path, "r", encoding="utf-8") as f:
            output = json.load(f)
        
        # Load the expected output
        with open(self.expected_output_path, "r", encoding="utf-8") as f:
            expected_output = json.load(f)
        
        # Check that the output has the correct structure
        self.assertIn("item", output, "Output does not contain 'item' key")
        
        # Check that "Comments" folder is not present
        folder_names = [item["name"] for item in output["item"]]
        self.assertNotIn("Comments", folder_names, 
                         f"'Comments' folder should not be present, found folders: {folder_names}")
        
        # Check that "Attachments" folder is present
        self.assertIn("Attachments", folder_names, 
                      f"'Attachments' folder should be present, found folders: {folder_names}")
        
        # Check that the output matches the expected condensed output
        self.assertEqual(output, expected_output, 
                         "Output does not match expected condensed output")


if __name__ == "__main__":
    unittest.main()