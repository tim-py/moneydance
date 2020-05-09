"""
Utilitly functions
"""


def elipses(string_in: str, length: int):
    if len(string_in) > length > 3:
        return string_in[:length - 3] + "..."
    return string_in[:length]
