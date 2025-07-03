import unittest
import json
import os
import subprocess
import tempfile
import pathlib
import shutil

class TestEndpointTypeFiltering(unittest.TestCase):
    """Tests for the --only-endpoints-type parameter functionality."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()

        # Get the path to the current file's directory
        current_file_dir = pathlib.Path(__file__).parent.absolute()
        
        # Construct the path to the test data file
        test_data_dir = os.path.join(current_file_dir, "conformance_tests", "test_data")
        if not os.path.exists(test_data_dir):
            test_data_dir = os.path.join(current_file_dir, "test_data")
        self.example_collection_path = os.path.join(
            test_data_dir,
            "wrike_postman_example.json")

        # Create a copy of the example collection in the test directory
        with open(self.example_collection_path, 'r') as f:
            self.example_collection = json.load(f)
        
        self.input_file = os.path.join(self.test_dir, "input_collection.json")
        with open(self.input_file, 'w') as f:
            json.dump(self.example_collection, f)
        
        # Path for output file
        self.output_file = os.path.join(self.test_dir, "output_collection.json")

    def tearDown(self):
        """Clean up after tests."""
        # Remove temporary directory and its contents
        shutil.rmtree(self.test_dir)

    def run_app_with_params(self, params):
        """Run the application with the given parameters."""
        cmd = ["python", "generate_postman_collection_subset.py"] + params
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result

    def test_valid_endpoint_types(self):
        """Test that valid endpoint types are accepted."""
        valid_types = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
        
        for endpoint_type in valid_types:
            params = [
                "--input-file", self.input_file,
                "--output-file", self.output_file,
                "--only-endpoints-type", endpoint_type
            ]
            
            result = self.run_app_with_params(params)
            
            self.assertEqual(result.returncode, 0, 
                f"Application failed with valid endpoint type {endpoint_type}. Error: {result.stderr}")
            
            # Check that output file was created
            self.assertTrue(os.path.exists(self.output_file), 
                f"Output file was not created for endpoint type {endpoint_type}")

    def test_invalid_endpoint_type(self):
        """Test that invalid endpoint types are rejected."""
        invalid_type = "INVALID_TYPE"
        params = [
            "--input-file", self.input_file,
            "--output-file", self.output_file,
            "--only-endpoints-type", invalid_type
        ]
        
        result = self.run_app_with_params(params)
        
        # The application should exit with a non-zero code for invalid input
        self.assertNotEqual(result.returncode, 0, 
            f"Application accepted invalid endpoint type {invalid_type}")
        
        # Check error message contains information about valid choices (using "choose from" phrase)
        self.assertIn("choose from", result.stderr.lower(), 
            "Error message doesn't mention valid choices")

    def test_get_endpoint_filtering(self):
        """Test that only GET endpoints are included when filtering for GET."""
        params = [
            "--input-file", self.input_file,
            "--output-file", self.output_file,
            "--only-endpoints-type", "GET"
        ]
        
        result = self.run_app_with_params(params)
        self.assertEqual(result.returncode, 0, f"Application failed. Error: {result.stderr}")
        
        # Load the output file
        with open(self.output_file, 'r') as f:
            filtered_collection = json.load(f)
        
        # Verify that only GET endpoints remain
        self._verify_only_endpoints_of_type(filtered_collection, "GET")

    def test_post_endpoint_filtering(self):
        """Test that only POST endpoints are included when filtering for POST."""
        params = [
            "--input-file", self.input_file,
            "--output-file", self.output_file,
            "--only-endpoints-type", "POST"
        ]
        
        result = self.run_app_with_params(params)
        self.assertEqual(result.returncode, 0, f"Application failed. Error: {result.stderr}")
        
        # Load the output file
        with open(self.output_file, 'r') as f:
            filtered_collection = json.load(f)
        
        # Verify that only POST endpoints remain
        self._verify_only_endpoints_of_type(filtered_collection, "POST")

    def test_no_matching_endpoints(self):
        """Test filtering with an endpoint type that doesn't exist in the collection."""
        # Create a collection with only GET endpoints
        get_only_collection = self._create_collection_with_only_type("GET")
        get_only_file = os.path.join(self.test_dir, "get_only_collection.json")
        with open(get_only_file, 'w') as f:
            json.dump(get_only_collection, f)
        
        params = [
            "--input-file", get_only_file,
            "--output-file", self.output_file,
            "--only-endpoints-type", "POST"
        ]
        
        result = self.run_app_with_params(params)
        self.assertEqual(result.returncode, 0, f"Application failed. Error: {result.stderr}")
        
        # Load the output file
        with open(self.output_file, 'r') as f:
            filtered_collection = json.load(f)
        
        # Verify that the collection has no items or has empty item arrays
        self._verify_empty_or_no_items(filtered_collection)

    def test_combined_parameters(self):
        """Test that --only-endpoints-type works with --remove-descriptions."""
        params = [
            "--input-file", self.input_file,
            "--output-file", self.output_file,
            "--only-endpoints-type", "GET",
            "--remove-descriptions"
        ]
        
        result = self.run_app_with_params(params)
        self.assertEqual(result.returncode, 0, f"Application failed. Error: {result.stderr}")
        
        # Load the output file
        with open(self.output_file, 'r') as f:
            filtered_collection = json.load(f)
        
        # Verify that only GET endpoints remain
        self._verify_only_endpoints_of_type(filtered_collection, "GET")
        
        # Verify that descriptions are removed
        self._verify_no_descriptions(filtered_collection)

    def _verify_only_endpoints_of_type(self, collection, endpoint_type):
        """Verify that all endpoints in the collection are of the specified type."""
        def check_items(items):
            for item in items:
                if "item" in item:
                    # This is a folder, check its items
                    if item["item"]:  # Only check if item array is not empty
                        check_items(item["item"])
                elif "request" in item:
                    # This is an endpoint
                    if isinstance(item["request"], dict) and "method" in item["request"]:
                        self.assertEqual(item["request"]["method"], endpoint_type,
                            f"Found endpoint with method {item['request']['method']}, expected {endpoint_type}")
        
        if "item" in collection:
            check_items(collection["item"])

    def _verify_empty_or_no_items(self, collection):
        """Verify that the collection has no items or has empty item arrays."""
        def check_items_empty(items):
            if not items:
                return
            for item in items:
                if "item" in item:
                    # This is a folder, it should either be empty or all its items should be empty
                    if item["item"]:  # Only check if item array is not empty
                        check_items_empty(item["item"])
                else:
                    # This should not happen - there should be no endpoints
                    self.fail(f"Found unexpected endpoint: {item}")
        
        if collection is None:
            return  # If collection is None, it means no matching endpoints were found
        
        if "item" in collection:
            # The top-level item array might be empty or contain only folders with empty item arrays
            if collection["item"]:
                check_items_empty(collection["item"])

    def _verify_no_descriptions(self, obj):
        """Verify that no 'description' fields exist in the object."""
        if isinstance(obj, dict):
            self.assertNotIn("description", obj, "Found 'description' field that should have been removed")
            for key, value in obj.items():
                self._verify_no_descriptions(value)
        elif isinstance(obj, list):
            for item in obj:
                self._verify_no_descriptions(item)

    def _create_collection_with_only_type(self, endpoint_type):
        """Create a modified collection with only endpoints of the specified type."""
        # Deep copy the example collection
        collection = json.loads(json.dumps(self.example_collection))
        
        # Modify all endpoints to have the specified type
        def modify_items(items):
            for item in items:
                if "item" in item:
                    # This is a folder, modify its items
                    modify_items(item["item"])
                elif "request" in item:
                    # This is an endpoint, modify its method
                    if isinstance(item["request"], dict):
                        item["request"]["method"] = endpoint_type
        
        if "item" in collection:
            modify_items(collection["item"])
        
        return collection


if __name__ == '__main__':
    unittest.main()