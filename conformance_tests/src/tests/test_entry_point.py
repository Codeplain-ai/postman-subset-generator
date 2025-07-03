#!/usr/bin/env python3
"""
Conformance tests for the entry point of the application.
"""
import unittest
import os
import sys
import subprocess
import importlib.util
from unittest.mock import patch
import tempfile


class TestEntryPoint(unittest.TestCase):
    """Test cases for the application entry point."""

    def setUp(self):
        """Set up the test environment."""
        # Create temporary files for testing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.input_file = os.path.join(self.temp_dir.name, "input.json")
        self.output_file = os.path.join(self.temp_dir.name, "output.json")
        
        # Copy the test data to the input file
        test_data_path = os.path.join(os.path.dirname(__file__), "wrike_postman_example.json")
        with open(test_data_path, 'r') as src, open(self.input_file, 'w') as dst:
            dst.write(src.read())
        self.script_path = "generate_postman_collection_subset.py"
        
    def test_script_exists(self):
        """Test that the script file exists."""
        self.assertTrue(
            os.path.isfile(self.script_path),
            f"Script file '{self.script_path}' does not exist"
        )

    def test_main_function_returns_zero_on_success(self):
        """Test that the main function returns 0 when executed successfully."""
        # Import the script as a module
        spec = importlib.util.spec_from_file_location("app_module", self.script_path)
        app_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(app_module)

        # Mock the argument parser to provide the required arguments
        with patch.object(app_module, 'parse_arguments') as mock_parse_args:
            mock_parse_args.return_value = type('Args', (), {'input_file': self.input_file, 'output_file': self.output_file, 'remove_descriptions': False, 'only_endpoints_type': None, 'whitelist_folders': None})
            
            result = app_module.main()
        
        self.assertEqual(
            result, 0,
            "The main function should return 0 on successful execution"
        )
        
    def test_remove_descriptions_flag(self):
        """Test that the --remove-descriptions flag works correctly."""
        # Import the script as a module
        spec = importlib.util.spec_from_file_location("app_module", self.script_path)
        app_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(app_module)

        # Mock the argument parser to provide the required arguments with remove_descriptions=True
        with patch.object(app_module, 'parse_arguments') as mock_parse_args:
            mock_parse_args.return_value = type('Args', (), {
                'input_file': self.input_file, 
                'output_file': self.output_file,
                'only_endpoints_type': None,
                'remove_descriptions': True,
                'whitelist_folders': None
            })
            
            result = app_module.main()
        
        self.assertEqual(
            result, 0,
            "The main function should return 0 when executed with --remove-descriptions flag"
        )
        
        # Verify that the output file was created
        self.assertTrue(os.path.exists(self.output_file),
                       f"Output file was not created at {self.output_file}")

    def test_only_endpoints_type_flag(self):
        """Test that the --only-endpoints-type flag works correctly."""
        # Import the script as a module
        spec = importlib.util.spec_from_file_location("app_module", self.script_path)
        app_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(app_module)

        # Mock the argument parser to provide the required arguments with only_endpoints_type='GET'
        with patch.object(app_module, 'parse_arguments') as mock_parse_args:
            mock_parse_args.return_value = type('Args', (), {
                'input_file': self.input_file, 
                'output_file': self.output_file, 
                'remove_descriptions': False,
                'only_endpoints_type': 'GET',
                'whitelist_folders': None
            })
            
            result = app_module.main()
        
        self.assertEqual(
            result, 0,
            "The main function should return 0 when executed with --only-endpoints-type flag"
        )
        self.assertTrue(os.path.exists(self.output_file),
                       f"Output file was not created at {self.output_file}")

    def test_whitelist_folders_flag(self):
        """Test that the --whitelist-folders flag works correctly."""
        # Create a temporary whitelist file
        whitelist_file = os.path.join(self.temp_dir.name, "whitelist.json")
        with open(whitelist_file, 'w') as f:
            f.write('{"folders": ["Attachments", "Comments"]}')
        
        # Import the script as a module
        spec = importlib.util.spec_from_file_location("app_module", self.script_path)
        app_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(app_module)

        # Mock the argument parser to provide the required arguments with whitelist_folders
        with patch.object(app_module, 'parse_arguments') as mock_parse_args:
            mock_parse_args.return_value = type('Args', (), {
                'input_file': self.input_file, 
                'output_file': self.output_file, 
                'remove_descriptions': False,
                'only_endpoints_type': None,
                'whitelist_folders': whitelist_file
            })
            
            # Mock the read_whitelist_folders function to return a predefined list
            with patch.object(app_module, 'read_whitelist_folders', return_value=["Attachments", "Comments"]):
                result = app_module.main()
        
        self.assertEqual(
            result, 0,
            "The main function should return 0 when executed with --whitelist-folders flag"
        )
        
        # Verify that the output file was created
        self.assertTrue(os.path.exists(self.output_file),
                       f"Output file was not created at {self.output_file}")

    def test_script_execution_as_subprocess(self):
        """Test that the script can be executed as a subprocess and returns a successful exit code."""
        # Run the script with the required arguments
        result = subprocess.run(
            [sys.executable, self.script_path, 
             "--input-file", self.input_file, 
             "--output-file", self.output_file],
            capture_output=True,
            text=True
        )
        
        self.assertEqual(
            result.returncode, 0,
            f"Script execution failed with return code {result.returncode}. "
            f"Stdout: {result.stdout}, Stderr: {result.stderr}"
        )
        
        # Verify that the output file was created
        self.assertTrue(
            os.path.exists(self.output_file),
            f"Output file was not created at {self.output_file}"
        )
        
        # Verify that the output file contains valid JSON
        with open(self.output_file, 'r') as f:
            import json
            try:
                json.load(f)
            except json.JSONDecodeError as e:
                self.fail(f"Output file does not contain valid JSON: {e}")

    def test_error_handling(self):
        """Test that the application handles exceptions properly and returns a non-zero exit code."""
        # Import the script as a module
        spec = importlib.util.spec_from_file_location("app_module", self.script_path)
        app_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(app_module)
        
        # Mock the argument parser to provide the required arguments
        with patch.object(app_module, 'parse_arguments') as mock_parse_args:
            mock_parse_args.return_value = type('Args', (), {'input_file': self.input_file, 'output_file': self.output_file, 'remove_descriptions': False, 'only_endpoints_type': None, 'whitelist_folders': None})
            
        with patch.object(app_module, 'setup_logging', side_effect=Exception("Test exception")):
            result = app_module.main()
            
            self.assertNotEqual(
                result, 0,
                "The main function should return a non-zero value when an exception occurs"
            )
            self.assertEqual(
                result, 1,
                "The main function should return 1 when an exception occurs"
            )

    def test_file_not_found_error(self):
        """Test that the script returns a non-zero exit code when the input file is not found."""
        # Use a non-existent input file
        non_existent_file = os.path.join(self.temp_dir.name, "non_existent.json")
        
        # Run the script with a non-existent input file
        result = subprocess.run(
            [sys.executable, self.script_path, 
             "--input-file", non_existent_file, 
             "--output-file", self.output_file],
            capture_output=True,
            text=True
        )
        
        self.assertEqual(
            result.returncode, 2,  # FileNotFoundError should return 2
            f"The script should return exit code 2 when the input file is not found. Got {result.returncode}"
        )

    def test_invalid_json_error(self):
        """Test that the script returns a non-zero exit code when the input file contains invalid JSON."""
        # Create a file with invalid JSON
        invalid_json_file = os.path.join(self.temp_dir.name, "invalid.json")
        with open(invalid_json_file, 'w') as f:
            f.write("{invalid json")
            
        # Run the script with the invalid JSON file
        result = subprocess.run(
            [sys.executable, self.script_path, 
             "--input-file", invalid_json_file, 
             "--output-file", self.output_file],
            capture_output=True,
            text=True
        )
        
        self.assertEqual(
            result.returncode, 3,  # JSONDecodeError should return 3
            f"The script should return exit code 3 when the input file contains invalid JSON. Got {result.returncode}"
        )

    def tearDown(self):
        """Clean up the test environment."""
        self.temp_dir.cleanup()


if __name__ == '__main__':
    unittest.main()