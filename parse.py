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
    try:
        group = inside_parenthesis.search(r"\(.+\)", s).group()
    except AttributeError:
        return ""
    else:
        return group[1:-1]
