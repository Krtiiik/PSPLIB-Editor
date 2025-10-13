from dataclasses import field


def hidden_field(default=None, **kwargs):
    return field(default=default, init=False, repr=False, compare=False, **kwargs)
