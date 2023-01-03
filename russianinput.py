from prompt_toolkit import prompt
from prompt_toolkit.document import Document
from prompt_toolkit.validation import Validator, ValidationError


class RussianValidator(Validator):
    "Validates that all the symbols in an input are from russian alphabet"
    lower_case = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
    upper_letters = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
    valid_symbols = lower_case + upper_letters + " "
    valid_symbols = set(list(valid_symbols))

    def __init__(self, allow_comma: bool = False) -> None:
        super().__init__()
        if allow_comma:
            self.valid_symbols |= {","}

    def validate(self, document: Document) -> None:
        for i, s in enumerate(document.text):
            if s not in self.valid_symbols:
                raise ValidationError(
                    message="This input contains symbols out of Russian alphabet.",
                    cursor_position=i
                )


def prompt_russian(
        message: str = "> ",
        allow_coma: bool = False,
        **kwargs
):
    "Prompts an input in Russian from the user."
    return prompt(
        message,
        validator=RussianValidator(allow_coma),
        complete_while_typing=False,
        mouse_support=True,
        **kwargs
    ).strip()


if __name__ == "__main__":
    prompt_russian("Test the russian prompt: ")
