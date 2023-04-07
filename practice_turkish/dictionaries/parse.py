import re


inside_parenthesis_pattern = re.compile(r"\(.+\)")


def inside_parenthesis(s: str) -> str:
    """Extract a part of the string s between parenthesis.

    Used to extract hint, clarifications or alternate translations within
    dictionary entry.

    Parameters
    ----------
    s : str
        Text to be searched in.

    Returns
    ----------
    t : str
        Text inside parenthesis.
    """
    match = inside_parenthesis_pattern.search(s)
    if match is None:
        return ""
    return match.group()[1:-1]
