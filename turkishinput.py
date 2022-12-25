from string import ascii_lowercase

from prompt_toolkit import prompt
from prompt_toolkit.document import Document
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.validation import Validator, ValidationError


turkish_letters = set(ascii_lowercase + "çğıöşü") - set("qxw")

nonlatin_letters = {
    "c": "ç",
    "g": "ğ",
    "i": "ı",
    "o": "ö",
    "s": "ş",
    "u": "ü"
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

    def validate(self, document: Document) -> None:
        for i, s in enumerate(document.text):
            if s.lower() not in turkish_letters:
                raise ValidationError(
                    message="This input contains symbols out of Turkish alphabet.",
                    cursor_position=i
                )


def prompt_turkish(message="> ", **kwargs):
    """
    Prompts an input in Turkish from the user. 
    Pressing TAB after letters 'c', 'g', 'i', 'o', 's' and 'u' 
    will prompt similar looking letters from Turkish alphabet.  
    """
    return prompt(
        message,
        completer=TurkishCompleter(),
        validator=TurkishValidator(),
        complete_while_typing=False,
        mouse_support=True,
        **kwargs
    )


if __name__ == "__main__":
    prompt_turkish("Test the Turkish prompt: ")
