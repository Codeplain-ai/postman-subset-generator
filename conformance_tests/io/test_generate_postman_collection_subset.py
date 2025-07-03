#!/usr/bin/env python3
"""
Conformance tests for the Postman Collection Subset Generator application.
"""
import unittest
import subprocess
import os
import json
import tempfile
import shutil
import pathlib


class TestPostmanCollectionSubsetGenerator(unittest.TestCase):
    """Test cases for the Postman Collection Subset Generator application."""

    def setUp(self):
        """Set up test environment before each test."""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()

        # Path to the example Postman Collection in the test_data directory
        current_dir = pathlib.Path(__file__).parent
        self.example_collection_path = os.path.join(
            current_dir, 
            "test_data", 
            "wrike_postman_example.json"
        )
        with open(self.example_collection_path, 'r', encoding='utf-8') as f:
            self.example_collection = json.load(f)
        
        self.test_input_path = os.path.join(self.test_dir, "test_input.json")
        with open(self.test_input_path, 'w', encoding='utf-8') as f:
            json.dump(self.example_collection, f, indent=2)
        
        # Path for the output file
        self.test_output_path = os.path.join(self.test_dir, "test_output.json")

    def tearDown(self):
        """Clean up test environment after each test."""
        # Remove the temporary directory and its contents
        shutil.rmtree(self.test_dir)

    def test_command_line_arguments(self):
        """Test that the app accepts the required command-line arguments."""
        # Run the app with the required arguments
        result = subprocess.run(
            [
                "python", 
                "generate_postman_collection_subset.py", 
                "--input-file", self.test_input_path, 
                "--output-file", self.test_output_path
            ],
            capture_output=True,
            text=True
        )
        
        # Check that the process completed successfully
        self.assertEqual(
            result.returncode, 0, 
            f"Application failed with return code {result.returncode}. "
            f"Stdout: {result.stdout}, Stderr: {result.stderr}"
        )

    def test_input_output_file_handling(self):
        """Test that the app reads from input file and writes to output file."""
        # Run the app
        result = subprocess.run(
            [
                "python", 
                "generate_postman_collection_subset.py", 
                "--input-file", self.test_input_path, 
                "--output-file", self.test_output_path
            ],
            capture_output=True,
            text=True
        )
        
        # Check that the process completed successfully
        self.assertEqual(
            result.returncode, 0, 
            f"Application failed with return code {result.returncode}. "
            f"Stdout: {result.stdout}, Stderr: {result.stderr}"
        )
        
        # Check that the output file was created
        self.assertTrue(
            os.path.exists(self.test_output_path), 
            f"Output file was not created at {self.test_output_path}"
        )
        
        # Check that the output file is not empty
        self.assertGreater(
            os.path.getsize(self.test_output_path), 0, 
            f"Output file at {self.test_output_path} is empty"
        )

    def test_content_preservation(self):
        """Test that the output file contains the same content as the input file."""
        # Run the app
        result = subprocess.run(
            [
                "python", 
                "generate_postman_collection_subset.py", 
                "--input-file", self.test_input_path, 
                "--output-file", self.test_output_path
            ],
            capture_output=True,
            text=True
        )
        
        # Check that the process completed successfully
        self.assertEqual(
            result.returncode, 0, 
            f"Application failed with return code {result.returncode}. "
            f"Stdout: {result.stdout}, Stderr: {result.stderr}"
        )
        
        # Load the output file
        with open(self.test_output_path, 'r', encoding='utf-8') as f:
            output_collection = json.load(f)
        
        # Compare the input and output collections
        self.assertEqual(
            self.example_collection, output_collection, 
            "Output collection does not match input collection"
        )
        
        # Check specific elements to ensure structure is preserved
        self.assertEqual(
            self.example_collection["info"]["name"], 
            output_collection["info"]["name"], 
            "Collection name was not preserved"
        )
        
        self.assertEqual(
            len(self.example_collection["item"]), 
            len(output_collection["item"]), 
            "Number of items was not preserved"
        )
        
        # Check that the auth section is preserved
        self.assertEqual(
            self.example_collection["auth"]["type"], 
            output_collection["auth"]["type"], 
            "Auth type was not preserved"
        )

    def test_error_handling_missing_input_file(self):
        """Test that the app handles missing input file appropriately."""
        # Path to a non-existent file
        nonexistent_file = os.path.join(self.test_dir, "nonexistent.json")
        
        # Run the app with a non-existent input file
        result = subprocess.run(
            [
                "python", 
                "generate_postman_collection_subset.py", 
                "--input-file", nonexistent_file, 
                "--output-file", self.test_output_path
            ],
            capture_output=True,
            text=True
        )
        
        # Check that the process failed
        self.assertNotEqual(
            result.returncode, 0, 
            f"Application unexpectedly succeeded with non-existent input file. "
            f"Stdout: {result.stdout}, Stderr: {result.stderr}"
        )
        
        # Check that the error message mentions the missing file
        self.assertIn(
            "not found", result.stderr.lower(), 
            f"Error message does not mention missing file. Stderr: {result.stderr}"
        )

    def test_error_handling_invalid_json(self):
        """Test that the app handles invalid JSON input appropriately."""
        # Create a file with invalid JSON
        invalid_json_path = os.path.join(self.test_dir, "invalid.json")
        with open(invalid_json_path, 'w', encoding='utf-8') as f:
            f.write("This is not valid JSON")
        
        # Run the app with the invalid JSON file
        result = subprocess.run(
            [
                "python", 
                "generate_postman_collection_subset.py", 
                "--input-file", invalid_json_path, 
                "--output-file", self.test_output_path
            ],
            capture_output=True,
            text=True
        )
        
        # Check that the process failed
        self.assertNotEqual(
            result.returncode, 0, 
            f"Application unexpectedly succeeded with invalid JSON input. "
            f"Stdout: {result.stdout}, Stderr: {result.stderr}"
        )
        
        # Check that the error message mentions JSON
        self.assertIn(
            "json", result.stderr.lower(), 
            f"Error message does not mention JSON issue. Stderr: {result.stderr}"
        )


if __name__ == "__main__":
    unittest.main()