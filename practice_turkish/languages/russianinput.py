from typing import Any

from prompt_toolkit import prompt
from prompt_toolkit.document import Document
from prompt_toolkit.validation import Validator, ValidationError


class RussianValidator(Validator):
    """A class used to validate an input in russian.

    Used by the `prompt` function from `prompt_toolkit` library to ensure that
    only permissible russian symbols are typed in by the user. Extends
    `Validator` class given by the library and overloads the `validate` method
    to check if all typed in symbols are permissible.
    """

    lower_case = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
    upper_letters = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
    valid_symbols = set(list(lower_case + upper_letters + " "))

    def __init__(self, additional_symbols: str = "") -> None:
        super().__init__()
        self.valid_symbols |= set(additional_symbols)

    def validate(self, document: Document) -> None:
        """Check if all typed in symbols are permissible.

        Parameters
        ----------
        document : Document
            A current state of prompting session.

        Raises
        ----------
        ValidationError
            If the document contains prohibited symbols.
        """
        for i, s in enumerate(document.text):
            if s not in self.valid_symbols:
                raise ValidationError(
                    message="This input contains symbols out of Russian alphabet.",
                    cursor_position=i,
                )


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
