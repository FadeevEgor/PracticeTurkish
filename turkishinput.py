from string import ascii_letters

from prompt_toolkit import prompt
from prompt_toolkit.document import Document
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.validation import Validator, ValidationError

from clipboard import copy_to_clipboard


nonlatin_letters = {
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
    "Completer for nonlatin letters in Turkish alphabet."

    def get_completions(self, document: Document, complete_event):
        active_letter = document.char_before_cursor
        try:
            suggestion = nonlatin_letters[active_letter]
        except KeyError:
            return None
        else:
            yield Completion(suggestion, start_position=-1)


class TurkishValidator(Validator):
    "Validates that all the symbols in an input are from Turkish alphabet"

    latin_letters = set(ascii_letters) - set("qQxXwW")
    non_latin_letters = set("âçÇğĞıIiİöÖşŞüÜ")
    valid_symbols = latin_letters | non_latin_letters | {" "}

    def __init__(self, additional_symbols: str = "") -> None:
        super().__init__()
        self.valid_symbols |= set(additional_symbols)

    def validate(self, document: Document) -> None:
        for i, s in enumerate(document.text):
            if s not in self.valid_symbols:
                raise ValidationError(
                    message="This input contains symbols out of Turkish alphabet.",
                    cursor_position=i
                )


def prompt_turkish(
    message: str = "> ",
    additional_symbols: str = "",
    **kwargs
) -> str:
    """
    Prompts an input in Turkish from the user. 
    Pressing TAB after letters 'c', 'g', 'i', 'o', 's' and 'u' 
    will prompt similar looking letters from Turkish alphabet.  
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
    while True:
        input_ = prompt_turkish("Test the Turkish prompt: ")
        if input_ == "":
            return
        copy_to_clipboard(input_)


if __name__ == "__main__":
    main()
