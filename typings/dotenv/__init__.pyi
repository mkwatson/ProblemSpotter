"""Type stubs for python-dotenv."""

from typing import Optional, Union

def load_dotenv(
    dotenv_path: Optional[Union[str, bytes]] = None,
    stream: Optional[object] = None,
    verbose: bool = False,
    override: bool = False,
    interpolate: bool = True,
    encoding: Optional[str] = None,
) -> bool:
    """Load environment variables from a .env file."""
    ...
