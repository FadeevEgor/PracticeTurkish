from typing import Any
from prompt_toolkit import prompt
from practice_turkish.languages.validator import SymbolValidator


class RussianValidator(SymbolValidator):
    """Validates russian input."""

    lower_case = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
    upper_letters = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
    valid_symbols = set(list(lower_case + upper_letters + " "))


def prompt_russian(
    message: str = "> ", additional_symbols: str = "", **kwargs: Any
) -> str:
    """Prompt an input in russian from the user.

    Parameters
    ----------
    message : str
        A text to be printed before the prompt. Defaults is "> ".
    additional_symbols : str
        A string of symbols, which should be considered valid, in addition
        to alphabet symbols and space.

    Returns
    ----------
    s : str
        A string typed in by the user.
    """
    return prompt(
        message,
        validator=RussianValidator(additional_symbols),
        complete_while_typing=False,
        mouse_support=True,
        **kwargs
    ).strip()


if __name__ == "__main__":
    prompt_russian("Test the russian prompt: ")
