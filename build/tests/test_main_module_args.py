"""
Unit tests for the command-line argument handling of the console application.
"""
import unittest
import sys
from unittest.mock import patch, MagicMock
import generate_postman_collection_subset
from tests.test_helpers import (
    SAMPLE_COLLECTION, 
    create_mock_args
)


class TestMainModuleArgs(unittest.TestCase):
    """Test cases for the command-line argument handling of generate_postman_collection_subset module."""

    @patch('argparse.ArgumentParser.parse_args')
    @patch('generate_postman_collection_subset.read_postman_collection')
    @patch('generate_postman_collection_subset.write_postman_subset')
    def test_main_with_args(self, mock_write, mock_read, mock_parse_args):
        """Test main function with command line arguments."""
        # Set up mocks
        mock_args = create_mock_args()
        mock_parse_args.return_value = mock_args
        mock_read.return_value = SAMPLE_COLLECTION

        # Call the main function
        result = generate_postman_collection_subset.main()

        # Verify the result and that the mocks were called correctly
        self.assertEqual(result, 0)
        mock_read.assert_called_once_with('input.json', unittest.mock.ANY)
        mock_write.assert_called_once_with(SAMPLE_COLLECTION, 'output.json', unittest.mock.ANY)

    @patch('argparse.ArgumentParser.parse_args')
    @patch('generate_postman_collection_subset.read_postman_collection')
    @patch('generate_postman_collection_subset.write_postman_subset')
    def test_main_with_remove_descriptions(self, mock_write, mock_read, mock_parse_args):
        """Test main function with --remove-descriptions flag."""
        # Set up mocks
        mock_args = create_mock_args(remove_descriptions=True)
        mock_parse_args.return_value = mock_args
        mock_read.return_value = SAMPLE_COLLECTION

        # Call the main function
        result = generate_postman_collection_subset.main()

        # Verify the result and that the mocks were called correctly
        self.assertEqual(result, 0)
        mock_write.assert_called_once()

    @patch('argparse.ArgumentParser.parse_args')
    @patch('generate_postman_collection_subset.read_postman_collection')
    @patch('generate_postman_collection_subset.filter_by_endpoint_type')
    @patch('generate_postman_collection_subset.write_postman_subset')
    def test_main_with_only_endpoints_type(self, mock_write, mock_filter, mock_read, mock_parse_args):
        """Test main function with --only-endpoints-type flag."""
        # Set up mocks
        mock_args = create_mock_args()
        mock_args.only_endpoints_type = "GET"
        mock_parse_args.return_value = mock_args
        mock_read.return_value = SAMPLE_COLLECTION
        mock_filter.return_value = {"filtered": "collection"}

        # Call the main function
        result = generate_postman_collection_subset.main()
        self.assertEqual(result, 0)
        mock_filter.assert_called_once_with(SAMPLE_COLLECTION, "GET", unittest.mock.ANY)

    @patch('argparse.ArgumentParser.parse_args')
    @patch('generate_postman_collection_subset.read_postman_collection')
    @patch('generate_postman_collection_subset.read_whitelist_folders')
    @patch('generate_postman_collection_subset.filter_by_whitelist_folders')
    @patch('generate_postman_collection_subset.write_postman_subset')
    def test_main_with_whitelist_folders(self, mock_write, mock_filter, mock_read_whitelist, mock_read, mock_parse_args):
        """Test main function with --whitelist-folders flag."""
        # Set up mocks
        mock_args = create_mock_args()
        mock_args.whitelist_folders = "whitelist.json"
        mock_parse_args.return_value = mock_args
        mock_read.return_value = SAMPLE_COLLECTION
        mock_read_whitelist.return_value = ["Folder1", "Folder2"]
        mock_filter.return_value = {"filtered": "collection"}

        # Call the main function
        result = generate_postman_collection_subset.main()
        self.assertEqual(result, 0)
        mock_filter.assert_called_once_with(SAMPLE_COLLECTION, ["Folder1", "Folder2"], unittest.mock.ANY)

    def test_parse_arguments(self):
        """Test argument parsing."""
        # Mock sys.argv
        test_args = ['script.py', '--input-file', 'input.json', '--output-file', 'output.json']
        with patch('sys.argv', test_args):
            args = generate_postman_collection_subset.parse_arguments()
            self.assertEqual(args.input_file, 'input.json')
            self.assertEqual(args.output_file, 'output.json')
            self.assertFalse(args.remove_descriptions)

        # Test with --only-endpoints-type flag
        test_args = ['script.py', '--input-file', 'input.json', '--output-file', 'output.json', '--only-endpoints-type', 'GET']
        with patch('sys.argv', test_args):
            args = generate_postman_collection_subset.parse_arguments()
            self.assertEqual(args.input_file, 'input.json')
            self.assertEqual(args.output_file, 'output.json')
            self.assertEqual(args.only_endpoints_type, 'GET')

        # Test with --remove-descriptions flag
        test_args = ['script.py', '--input-file', 'input.json', '--output-file', 'output.json', '--remove-descriptions']
        with patch('sys.argv', test_args):
            args = generate_postman_collection_subset.parse_arguments()
            self.assertEqual(args.input_file, 'input.json')
            self.assertEqual(args.output_file, 'output.json')
            self.assertTrue(args.remove_descriptions)

        # Test with --whitelist-folders flag
        test_args = ['script.py', '--input-file', 'input.json', '--output-file', 'output.json', '--whitelist-folders', 'whitelist.json']
        with patch('sys.argv', test_args):
            args = generate_postman_collection_subset.parse_arguments()
            self.assertEqual(args.input_file, 'input.json')
            self.assertEqual(args.output_file, 'output.json')
            self.assertEqual(args.whitelist_folders, 'whitelist.json')


if __name__ == '__main__':
    unittest.main()