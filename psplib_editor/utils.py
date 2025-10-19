from dataclasses import field
import io
from pathlib import Path
from typing import Callable, Concatenate, ParamSpec, Union


P = ParamSpec("P")


def hidden_field(default=None, **kwargs):
    """
    A dataclass field that is not included in the generated __init__, __repr__, and comparison methods.

    Args:
        default: The default value for the field.
        **kwargs: Additional keyword arguments to pass to the field function.

    Returns:
        A dataclass field with init, repr, and compare set to False.
    """
    return field(default=default, init=False, repr=False, compare=False, **kwargs)


def use_read_file(
    source: Union[str, Path, io.TextIOBase],
    action: Callable[Concatenate[io.TextIOBase, P], None],
    *args: P.args,
    **kwargs: P.kwargs,
    ) -> None:
    """
    Utility function to handle reading from a file or file-like object.

    Args:
        source: The source to read from.
        action: The action to perform on the source.
        *args: Positional arguments to pass to the action.
        **kwargs: Keyword arguments to pass to the action.
    """
    if isinstance(source, (str, Path)):
        with open(source, "r", encoding="utf-8") as f:
            return action(f, *args, **kwargs)
    elif isinstance(source, io.TextIOBase):
        return action(source, *args, **kwargs)
    else:
        raise TypeError("source must a filename, Path, or file-like object")


def use_write_file(
    target: Union[str, Path, io.TextIOBase],
    action: Callable[Concatenate[io.TextIOBase, P], None],
    *args: P.args,
    **kwargs: P.kwargs,
    ) -> None:
    """
    Utility function to handle writing to a file or file-like object.

    Args:
        target: The target to write to.
        action: The action to perform on the target.
        *args: Positional arguments to pass to the action.
        **kwargs: Keyword arguments to pass to the action.
    """
    if isinstance(target, (str, Path)):
        with open(target, "w", encoding="utf-8") as f:
            return action(f, *args, **kwargs)
    elif isinstance(target, io.TextIOBase):
        return action(target, *args, **kwargs)
    else:
        raise TypeError("target must a filename, Path, or file-like object")
