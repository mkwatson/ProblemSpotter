"""Type stubs for pydantic."""

from typing import Any, Callable, Dict, Optional, Type, TypeVar, Union

T = TypeVar("T", bound="BaseModel")

class BaseModel:
    """Base model for pydantic models."""

    def __init__(self, **data: Any) -> None: ...
    def dict(self, **kwargs: Any) -> Dict[str, Any]:
        """Return model as a dictionary."""
        ...

    @classmethod
    def parse_obj(cls: Type[T], obj: Dict[str, Any]) -> T:
        """Parse object from dictionary."""
        ...

def Field(
    default: Any = ...,
    default_factory: Optional[Callable[[], Any]] = None,
    alias: Optional[str] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    exclude: Union[bool, Any] = None,
    include: Union[bool, Any] = None,
    const: Optional[bool] = None,
    gt: Optional[float] = None,
    ge: Optional[float] = None,
    lt: Optional[float] = None,
    le: Optional[float] = None,
    multiple_of: Optional[float] = None,
    max_digits: Optional[int] = None,
    decimal_places: Optional[int] = None,
    min_items: Optional[int] = None,
    max_items: Optional[int] = None,
    unique_items: Optional[bool] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    regex: Optional[str] = None,
    **extra: Any,
) -> Any:
    """Field function for defining model fields."""
    ...
