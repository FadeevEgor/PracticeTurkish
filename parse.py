import re


def inside_parenthesis(s: str) -> str:
    """
    Extracts a part of the string s between parenthesis.
    Useful to extract alternate translation or hint in the format.
    """
    try:
        group = re.search(r"\(.+\)", s).group()
    except AttributeError:
        return ""
    else:
        return group[1:-1]
