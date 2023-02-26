from string import ascii_letters

from prompt_toolkit import prompt
from prompt_toolkit.document import Document
from prompt_toolkit.validation import Validator, ValidationError


class EnglishValidator(Validator):
    "Validates that all the symbols in an input are from english alphabet"
    valid_symbols = set(list(ascii_letters + " "))

    def __init__(self, additional_symbols: str = "") -> None:
        super().__init__()
        self.valid_symbols |= set(additional_symbols)

    def validate(self, document: Document) -> None:
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
    "Prompts an input in English from the user."
    return prompt(
        message,
        validator=EnglishValidator(additional_symbols),
        complete_while_typing=False,
        mouse_support=True,
        **kwargs
    ).strip()


if __name__ == "__main__":
    prompt_english("Test the english prompt: ")
