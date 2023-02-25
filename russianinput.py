from prompt_toolkit import prompt
from prompt_toolkit.document import Document
from prompt_toolkit.validation import Validator, ValidationError


class RussianValidator(Validator):
    "Validates that all the symbols in an input are from russian alphabet"
    lower_case = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
    upper_letters = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
    valid_symbols = set(list(lower_case + upper_letters + " "))

    def __init__(self, additional_symbols: str = "") -> None:
        super().__init__()
        self.valid_symbols |= set(additional_symbols)

    def validate(self, document: Document) -> None:
        for i, s in enumerate(document.text):
            if s not in self.valid_symbols:
                raise ValidationError(
                    message="This input contains symbols out of Russian alphabet.",
                    cursor_position=i
                )


def prompt_russian(
        message: str = "> ",
        additional_symbols: str = "",
        **kwargs
):
    "Prompts an input in Russian from the user."
    return prompt(
        message,
        validator=RussianValidator(additional_symbols),
        complete_while_typing=False,
        mouse_support=True,
        **kwargs
    ).strip()


if __name__ == "__main__":
    prompt_russian("Test the russian prompt: ")
