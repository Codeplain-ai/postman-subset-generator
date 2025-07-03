import unittest
import os
import json
import subprocess
import tempfile
import shutil

class TestRemoveDescriptions(unittest.TestCase):
    """Test cases for the --remove-descriptions functionality."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        
        # Path to the main script
        self.script_path = "generate_postman_collection_subset.py"
        
        # Ensure the script exists
        self.assertTrue(os.path.exists(self.script_path), 
                        f"Script not found at {self.script_path}")
        
        # Create test collections
        self.create_test_collections()

    def tearDown(self):
        """Clean up after tests."""
        # Remove temporary directory and its contents
        shutil.rmtree(self.test_dir)

    def create_test_collections(self):
        """Create test Postman Collections for testing."""
        # Simple collection with description at top level
        self.simple_collection = {
            "info": {
                "name": "Test Collection",
                "description": "This is a test description",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "item": []
        }
        
        # Collection with nested descriptions
        self.nested_collection = {
            "info": {
                "name": "Nested Test Collection",
                "description": "Top level description",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "item": [
                {
                    "name": "Folder",
                    "description": "Folder description",
                    "item": [
                        {
                            "name": "Request",
                            "description": "Request description",
                            "request": {
                                "method": "GET",
                                "url": "https://example.com",
                                "description": "URL description"
                            },
                            "response": []
                        }
                    ]
                }
            ]
        }
        
        # Minimal valid collection
        self.minimal_collection = {
            "info": {
                "name": "Minimal Collection",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "item": []
        }
        
        # Save collections to files
        self.simple_collection_path = os.path.join(self.test_dir, "simple_collection.json")
        self.nested_collection_path = os.path.join(self.test_dir, "nested_collection.json")
        self.minimal_collection_path = os.path.join(self.test_dir, "minimal_collection.json")
        self.example_collection_path = os.path.join(self.test_dir, "example_collection.json")
        
        with open(self.simple_collection_path, 'w') as f:
            json.dump(self.simple_collection, f)
        
        with open(self.nested_collection_path, 'w') as f:
            json.dump(self.nested_collection, f)
        
        with open(self.minimal_collection_path, 'w') as f:
            json.dump(self.minimal_collection, f)
        
        # Get the absolute path to the test resources directory
        test_dir = os.path.dirname(os.path.abspath(__file__))
        example_path = os.path.join(test_dir, "test_resources", "wrike_postman_example.json")
        
        # Copy the example collection from resources using absolute path
        with open(example_path, 'r') as src:
            example_collection = json.load(src)
            with open(self.example_collection_path, 'w') as dest:
                json.dump(example_collection, dest)

    def run_app(self, input_file, output_file, remove_descriptions=False):
        """Run the application with given parameters."""
        cmd = ["python", self.script_path, "--input-file", input_file, "--output-file", output_file]
        
        if remove_descriptions:
            cmd.append("--remove-descriptions")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        self.assertEqual(result.returncode, 0, 
                         f"Application failed with error: {result.stderr}")
        
        return result

    def count_descriptions(self, obj):
        """Count the number of 'description' fields in a JSON object recursively."""
        count = 0
        
        if isinstance(obj, dict):
            # Count description in current dict
            if 'description' in obj:
                count += 1
            
            # Recursively count in all values
            for value in obj.values():
                count += self.count_descriptions(value)
                
        elif isinstance(obj, list):
            # Recursively count in all list items
            for item in obj:
                count += self.count_descriptions(item)
                
        return count

    def test_descriptions_preserved_without_flag(self):
        """Test that descriptions are preserved when --remove-descriptions is not used."""
        output_file = os.path.join(self.test_dir, "output_preserved.json")
        
        # Run app without --remove-descriptions
        self.run_app(self.nested_collection_path, output_file)
        
        # Check output
        with open(output_file, 'r') as f:
            output = json.load(f)
        
        # Count descriptions in original and output
        original_count = self.count_descriptions(self.nested_collection)
        output_count = self.count_descriptions(output)
        
        self.assertEqual(output_count, original_count, 
                         f"Expected {original_count} descriptions, but found {output_count}")
        
        # Verify specific descriptions are preserved
        self.assertEqual(output["info"]["description"], "Top level description",
                         "Top level description should be preserved")
        
        self.assertEqual(output["item"][0]["description"], "Folder description",
                         "Folder description should be preserved")

    def test_top_level_descriptions_removed(self):
        """Test that top-level descriptions are removed when --remove-descriptions is used."""
        output_file = os.path.join(self.test_dir, "output_top_level.json")
        
        # Run app with --remove-descriptions
        self.run_app(self.simple_collection_path, output_file, remove_descriptions=True)
        
        # Check output
        with open(output_file, 'r') as f:
            output = json.load(f)
        
        # Verify description is removed
        self.assertNotIn("description", output["info"], 
                         "Top level description should be removed")

    def test_nested_descriptions_removed(self):
        """Test that nested descriptions are removed when --remove-descriptions is used."""
        output_file = os.path.join(self.test_dir, "output_nested.json")
        
        # Run app with --remove-descriptions
        self.run_app(self.nested_collection_path, output_file, remove_descriptions=True)
        
        # Check output
        with open(output_file, 'r') as f:
            output = json.load(f)
        
        # Count descriptions in output
        description_count = self.count_descriptions(output)
        
        self.assertEqual(description_count, 0, 
                         f"Expected 0 descriptions, but found {description_count}")
        
        # Verify specific descriptions are removed
        self.assertNotIn("description", output["info"], 
                         "Top level description should be removed")
        
        self.assertNotIn("description", output["item"][0], 
                         "Folder description should be removed")
        
        self.assertNotIn("description", output["item"][0]["item"][0], 
                         "Request description should be removed")
        
        self.assertNotIn("description", output["item"][0]["item"][0]["request"], 
                         "URL description should be removed")

    def test_complex_descriptions_removed(self):
        """Test that descriptions in complex structures are removed when --remove-descriptions is used."""
        output_file = os.path.join(self.test_dir, "output_complex.json")
        
        # Run app with --remove-descriptions
        self.run_app(self.example_collection_path, output_file, remove_descriptions=True)
        
        # Check output
        with open(output_file, 'r') as f:
            output = json.load(f)
        
        # Count descriptions in output
        description_count = self.count_descriptions(output)
        
        self.assertEqual(description_count, 0, 
                         f"Expected 0 descriptions, but found {description_count}")

    def test_minimal_collection_handled_correctly(self):
        """Test that minimal collections are handled correctly."""
        output_file = os.path.join(self.test_dir, "output_minimal.json")
        
        # Run app with --remove-descriptions
        self.run_app(self.minimal_collection_path, output_file, remove_descriptions=True)
        
        # Check output
        with open(output_file, 'r') as f:
            output = json.load(f)
        
        # Verify the structure is preserved
        self.assertIn("info", output, "Output should contain 'info' field")
        self.assertIn("name", output["info"], "Output should contain 'name' field")
        self.assertIn("schema", output["info"], "Output should contain 'schema' field")
        self.assertIn("item", output, "Output should contain 'item' field")


if __name__ == '__main__':
    unittest.main()