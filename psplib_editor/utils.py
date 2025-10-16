from dataclasses import field


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
