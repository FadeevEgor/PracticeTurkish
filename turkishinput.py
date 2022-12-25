from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion


nonlatin_letters = {
    "c": ["c", "ç"],
    "g": ["g", "ğ"],
    "i": ["i", "ı"],
    "o": ["o", "ö"],
    "s": ["s", "ş"],
    "u": ["u", "ü"]
}


class TurkishCompleter(Completer):

    def get_completions(self, document, complete_event):
        active_letter = document.char_before_cursor
        try:
            for suggestion in nonlatin_letters[active_letter]:
                yield Completion(suggestion, start_position=-1)
        except KeyError:
            return None


def prompt_turkish(message):
    return prompt(message, completer=TurkishCompleter(), complete_while_typing=False)
