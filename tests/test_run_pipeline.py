"""Tests for the run_pipeline module."""

import os
import tempfile
from unittest.mock import MagicMock, patch

import run_pipeline


class TestRunPipeline:
    """Test cases for the run_pipeline module."""

    @patch("run_pipeline.fetch_problems")
    @patch("run_pipeline.analyze_problems")
    @patch("run_pipeline.os.path.getmtime")
    @patch("run_pipeline.os.listdir")
    def test_pipeline_full_run(
        self,
        mock_listdir: MagicMock,
        mock_getmtime: MagicMock,
        mock_analyze_problems: MagicMock,
        mock_fetch_problems: MagicMock,
    ) -> None:
        """Test the full pipeline run."""
        # Set up mocks
        mock_fetch_problems.main.return_value = 0
        mock_analyze_problems.load_env_vars.return_value = {"api_key": "test_key"}
        mock_analyze_problems.analyze_file.return_value = "/path/to/output.json"

        # Mock file listing
        mock_listdir.return_value = ["reddit_how_do_i_results_20250404_113459.json"]
        mock_getmtime.return_value = 1743791490.0

        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock directories
            mock_analyze_problems.RAW_DATA_DIR = os.path.join(temp_dir, "raw")
            run_pipeline.fetch_problems.OUTPUT_DIR = temp_dir

            # Create directory structure
            os.makedirs(mock_analyze_problems.RAW_DATA_DIR, exist_ok=True)

            # Create a test file
            test_file_path = os.path.join(temp_dir, "reddit_how_do_i_results_20250404_113459.json")
            with open(test_file_path, "w") as f:
                f.write("[]")

            # Run the pipeline with no arguments (default full pipeline)
            with patch("sys.argv", ["run_pipeline.py"]):
                result = run_pipeline.main()

            # Verify result
            assert result == 0

            # Verify fetch was called
            mock_fetch_problems.main.assert_called_once()

            # Verify analyze was called
            mock_analyze_problems.analyze_file.assert_called_once()

    @patch("run_pipeline.fetch_problems")
    @patch("run_pipeline.analyze_problems")
    def test_pipeline_fetch_only(
        self, mock_analyze_problems: MagicMock, mock_fetch_problems: MagicMock
    ) -> None:
        """Test the pipeline with fetch only."""
        # Set up mocks
        mock_fetch_problems.main.return_value = 0

        # Run the pipeline with fetch-only flag
        with patch("sys.argv", ["run_pipeline.py", "--fetch-only"]):
            # Create a temporary directory for this test
            with tempfile.TemporaryDirectory() as temp_dir:
                # Mock directories
                mock_analyze_problems.RAW_DATA_DIR = os.path.join(temp_dir, "raw")
                run_pipeline.fetch_problems.OUTPUT_DIR = temp_dir

                # Create directory structure
                os.makedirs(mock_analyze_problems.RAW_DATA_DIR, exist_ok=True)

                # Run with mocked file listing
                with patch("run_pipeline.os.listdir") as mock_listdir:
                    with patch("run_pipeline.os.path.getmtime") as mock_getmtime:
                        # Mock file listing
                        mock_listdir.return_value = ["reddit_how_do_i_results_20250404_113459.json"]
                        mock_getmtime.return_value = 1743791490.0

                        # Create a test file
                        test_file_path = os.path.join(
                            temp_dir, "reddit_how_do_i_results_20250404_113459.json"
                        )
                        with open(test_file_path, "w") as f:
                            f.write("[]")

                        result = run_pipeline.main()

        # Verify result
        assert result == 0

        # Verify fetch was called
        mock_fetch_problems.main.assert_called_once()

        # Verify analyze was NOT called
        mock_analyze_problems.analyze_file.assert_not_called()

    @patch("run_pipeline.analyze_problems")
    def test_pipeline_analyze_only(self, mock_analyze_problems: MagicMock) -> None:
        """Test the pipeline with analyze only."""
        # Set up mocks
        mock_analyze_problems.load_env_vars.return_value = {"api_key": "test_key"}
        mock_analyze_problems.analyze_file.return_value = "/path/to/output.json"

        # Create a temporary directory for this test
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock directories
            mock_analyze_problems.RAW_DATA_DIR = os.path.join(temp_dir, "raw")

            # Create directory structure
            os.makedirs(mock_analyze_problems.RAW_DATA_DIR, exist_ok=True)

            # Create a test file
            test_file_path = os.path.join(
                mock_analyze_problems.RAW_DATA_DIR, "reddit_how_do_i_results_20250404_113459.json"
            )
            with open(test_file_path, "w") as f:
                f.write("[]")

            # Mock file listing
            with patch("run_pipeline.os.listdir") as mock_listdir:
                with patch("run_pipeline.os.path.getmtime") as mock_getmtime:
                    mock_listdir.return_value = ["reddit_how_do_i_results_20250404_113459.json"]
                    mock_getmtime.return_value = 1743791490.0

                    # Run the pipeline with analyze-only flag
                    with patch("sys.argv", ["run_pipeline.py", "--analyze-only"]):
                        result = run_pipeline.main()

        # Verify result
        assert result == 0

        # Verify analyze was called
        mock_analyze_problems.load_env_vars.assert_called_once()
        mock_analyze_problems.initialize_openai_client.assert_called_once()
        mock_analyze_problems.analyze_file.assert_called_once()
