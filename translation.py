import random
from operator import methodcaller, attrgetter
from typing import Iterable

import typer
from rich import print
from prompt_toolkit import prompt
from prompt_toolkit.document import Document
from prompt_toolkit.completion import Completer, Completion, CompleteEvent
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.auto_suggest import AutoSuggest, Suggestion

from turkishinput import prompt_turkish
from russianinput import prompt_russian
from turkrutdictionaryitem import TurkrutDictionaryItem


dictionary_item_types = {
    "turkrut": TurkrutDictionaryItem
}


def ask_target_language() -> str:
    options = {
        "Turkish to Russian": "russian",
        "Russian to Turkish": "turkish"
    }

    class LanguageCompleter(Completer):
        def get_completions(self, document: Document, complete_event: CompleteEvent) -> Iterable[Completion]:
            for option in options:
                yield Completion(option, start_position=-1000)

    class LanguageValidator(Validator):
        def validate(self, document: Document) -> None:
            if document.text not in options:
                raise ValidationError(
                    message="Not a valid option"
                )

    class LanguageSuggest(AutoSuggest):
        def get_suggestion(self, buffer: "Buffer", document: Document) -> Suggestion | None:
            # if Document.tex == "":
            return Suggestion("Turkish to Russian")

    option = prompt(
        "Choose a target language: ",
        # auto_suggest=LanguageSuggest(),
        completer=LanguageCompleter(),
        validator=LanguageValidator(),
        default="Turkish to Russian",
    )
    return options[option]


def practice_translation(
        filename: str,
        shuffle: bool = True,
        type: str = "turkrut"
):
    dict_item = dictionary_item_types[type]
    dictionary = []
    with open(filename, encoding="utf-8") as f:
        for line in f:
            dictionary.append(dict_item(line))
    if shuffle:
        random.shuffle(dictionary)

    target_language = ask_target_language()
    ask_translation = methodcaller(
        f"ask_translation_to_{target_language}"
    )
    answer_getter = attrgetter(target_language)
    for word in dictionary:
        is_correct = ask_translation(word)
        if is_correct:
            print(f"[green]Correct![/green]")
        else:
            correct_answer = answer_getter(word)
            print(
                f"[red]Incorrect![/red] Right answer: [green]{correct_answer}[/green]"
            )


if __name__ == "__main__":
    typer.run(practice_translation)
