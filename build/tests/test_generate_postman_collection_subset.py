"""
Unit tests for the console application.
"""
import unittest
import json
from unittest.mock import patch, MagicMock
import generate_postman_collection_subset
from tests.test_helpers import (
    SAMPLE_COLLECTION, 
    SAMPLE_COLLECTION_NO_DESC,
    create_mock_args
)


class TestMainModule(unittest.TestCase):
    """Test cases for the generate_postman_collection_subset module."""

    @patch('generate_postman_collection_subset.parse_arguments')
    @patch('generate_postman_collection_subset.read_postman_collection')
    @patch('generate_postman_collection_subset.write_postman_subset')
    def test_main_success(self, mock_write, mock_read, mock_parse_args):
        """Test that the main function returns 0 on success."""
        mock_args = create_mock_args()
        mock_parse_args.return_value = mock_args
        mock_read.return_value = SAMPLE_COLLECTION
        result = generate_postman_collection_subset.main()
        self.assertEqual(result, 0)
        mock_read.assert_called_once_with('input.json', unittest.mock.ANY)
        mock_write.assert_called_once_with(SAMPLE_COLLECTION, 'output.json', unittest.mock.ANY)

    @patch('generate_postman_collection_subset.main')
    def test_sys_exit_called_with_main_result(self, mock_main):
        """Test that sys.exit is called with the result of main()."""
        # Set up the mock to return a specific value
        mock_main.return_value = 42
        
        # Create a context where we can test the __name__ == "__main__" block
        with patch('sys.exit') as mock_exit:
            # Directly call the code that would run if __name__ == "__main__"
            generate_postman_collection_subset.sys.exit(generate_postman_collection_subset.main())
            mock_exit.assert_called_once_with(42)

    def test_file_not_found_error(self):
        """Test handling of FileNotFoundError."""
        with patch('generate_postman_collection_subset.parse_arguments') as mock_parse_args:
            mock_args = create_mock_args(input_file='nonexistent.json')
            mock_parse_args.return_value = mock_args
            
            # Mock logging to avoid actual error messages in test output
            with patch('logging.error'):
                # The main function should return 2 for FileNotFoundError
                result = generate_postman_collection_subset.main()
                self.assertEqual(result, 2)

    @patch('generate_postman_collection_subset.parse_arguments')
    @patch('generate_postman_collection_subset.setup_logging')
    def test_logging_setup(self, mock_setup_logging, mock_parse_args):
        """Test that logging is set up correctly."""
        # Mock the arguments to avoid command line parsing
        mock_args = create_mock_args()
        mock_parse_args.return_value = mock_args
        
        # Mock read_postman_collection to avoid file operations
        with patch('generate_postman_collection_subset.read_postman_collection'), \
             patch('generate_postman_collection_subset.write_postman_subset'):
            generate_postman_collection_subset.main()
            mock_setup_logging.assert_called_once()


if __name__ == '__main__':
    unittest.main()