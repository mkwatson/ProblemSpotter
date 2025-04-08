"""Test the __main__ module."""


def test_main_import() -> None:
    """Test that __main__ module imports run_pipeline.main correctly."""
    # Import here to avoid early import issues
    from problem_spotter.__main__ import main
    from problem_spotter.core.run_pipeline import main as pipeline_main

    # Verify that the imported main function is the same as run_pipeline.main
    assert main is pipeline_main
