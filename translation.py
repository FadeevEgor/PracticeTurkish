import random
from operator import methodcaller, attrgetter
from typing import Iterable

from rich import print
from prompt_toolkit import prompt
from prompt_toolkit.document import Document
from prompt_toolkit.completion import Completer, Completion, CompleteEvent
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.auto_suggest import AutoSuggest, Suggestion
import typer
from InquirerPy import inquirer

from turkishinput import prompt_turkish
from russianinput import prompt_russian
from turkrutdictionaryitem import TurkrutDictionaryItem


dictionary_item_types = {
    "turkrut": TurkrutDictionaryItem
}


def prompt_target_language():
    choice = inquirer.select(
        message="Choose language you want to translate to.",
        choices=["Turkish → Russian", "Russian → Turkish"],
    ).execute()
    return choice.lower().split(" → ")[-1]


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

    target_language = prompt_target_language()
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
