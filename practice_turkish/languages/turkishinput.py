from string import ascii_letters
from typing import Generator, Any

from prompt_toolkit import prompt
from prompt_toolkit.document import Document
from prompt_toolkit.completion import Completer, Completion, CompleteEvent

from practice_turkish.languages.clipboard import copy_to_clipboard
from practice_turkish.languages.validator import SymbolValidator

non_latin_letters = {
    "a": "â",
    "c": "ç",
    "C": "Ç",
    "g": "ğ",
    "G": "Ğ",
    "i": "ı",
    "I": "İ",
    "o": "ö",
    "O": "Ö",
    "s": "ş",
    "S": "Ş",
    "u": "ü",
    "U": "Ü",
}


class TurkishCompleter(Completer):
    """A class used in order to type nonlatin letters from Turkish alphabet.

    Used by the `prompt` function from `prompt_toolkit` library in order to
    generate completions, which allow to type in all letters from turkish
    alphabet with only en-US layout keyboard. Pressing tab after letters
    'c', 'g', 'i', 'o', 's' and 'u' offers completion with "ç", "ğ", "ı",
    "ö", "ş" and "ü".
    """

    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> Generator[Completion, None, None]:
        "Generator yielding completions for the symbol right before the cursor"
        active_letter = document.char_before_cursor
        try:
            suggestion = non_latin_letters[active_letter]
        except KeyError:
            return
        yield Completion(suggestion, start_position=-1)


class TurkishValidator(SymbolValidator):
    """A class used to validate an input in turkish."""

    latin_letters = set(ascii_letters) - set("qQxXwW")
    non_latin_letters = set("âçÇğĞıIiİöÖşŞüÜ")
    valid_symbols = latin_letters | non_latin_letters | {" "}


def prompt_turkish(
    message: str = "> ", additional_symbols: str = "", **kwargs: Any
) -> str:
    """Prompt an input in turkish from the user.

    Prompts an input in Turkish from the user.
    Pressing TAB after letters 'c', 'g', 'i', 'o', 's' and 'u' will offer
    similar looking letters from Turkish alphabet as a replacement.

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
        completer=TurkishCompleter(),
        validator=TurkishValidator(additional_symbols),
        complete_while_typing=False,
        mouse_support=True,
        **kwargs
    ).strip()


def main() -> None:
    """If open as a script, run make number function."""
    while True:
        input_ = prompt_turkish("Test the Turkish prompt: ")
        if input_ == "":
            return
        copy_to_clipboard(input_)


if __name__ == "__main__":
    main()
