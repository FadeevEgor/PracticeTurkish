from prompt_toolkit import prompt
from prompt_toolkit.document import Document
from prompt_toolkit.validation import Validator, ValidationError


class RussianValidator(Validator):
    "Validates that all the symbols in an input are from russian alphabet"

    def validate(self, document: Document) -> None:
        valid_letters = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
        for i, s in enumerate(document.text):
            if s not in valid_letters:
                raise ValidationError(
                    message="This input contains symbols out of Russian alphabet.",
                    cursor_position=i
                )


def prompt_russian(message="> ", **kwargs):
    "Prompts an input in Russian from the user."
    return prompt(
        message,
        validator=RussianValidator(),
        complete_while_typing=False,
        mouse_support=True,
        **kwargs
    )


if __name__ == "__main__":
    prompt_russian("Test the russian prompt: ")
