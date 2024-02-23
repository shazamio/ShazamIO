from typing import Callable, Any, TypeVar, cast
import functools
import warnings

F = TypeVar("F", bound=Callable[..., Any])


def deprecated(reason: str) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def new_func(*args: Any, **kwargs: Any) -> Any:
            warnings.simplefilter("always", DeprecationWarning)
            warnings.warn(
                f"Call to deprecated function {func.__name__}. {reason}",
                category=DeprecationWarning,
                stacklevel=2,
            )
            warnings.simplefilter("default", DeprecationWarning)
            return func(*args, **kwargs)

        return cast(F, new_func)

    return decorator
