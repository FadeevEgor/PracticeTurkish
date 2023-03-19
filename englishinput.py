from string import ascii_letters

from prompt_toolkit import prompt
from prompt_toolkit.document import Document
from prompt_toolkit.validation import Validator, ValidationError


class EnglishValidator(Validator):
    """A class used to validate an input in english.

    Used by the `prompt` function from `prompt_toolkit` library to ensure that 
    only permissible english symbols are typed in by the user. Extends 
    `Validator` class given by the library and overloads the `validate` method
    to check if all typed in symbols are permissible.
    """
    valid_symbols = set(list(ascii_letters + " "))

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
                    message="This input contains symbols out of english alphabet.",
                    cursor_position=i
                )


def prompt_english(
        message: str = "> ",
        additional_symbols: str = "",
        **kwargs
) -> str:
    """Prompt an input in English from the user.

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
        validator=EnglishValidator(additional_symbols),
        complete_while_typing=False,
        mouse_support=True,
        **kwargs
    ).strip()


if __name__ == "__main__":
    prompt_english("Test the english prompt: ")
