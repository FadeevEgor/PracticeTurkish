import random
from operator import is_
from typing import Type
from pathlib import Path

from rich import print
import typer
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.validator import PathValidator

from dictionaryitem import DictionaryItem
from turkrutdictionaryitem import TurkrutDictionaryItem


def prompt_filename():
    return inquirer.filepath(
        message="Enter file to practice: ",
        default=str(Path.cwd()) + "\\",
        validate=PathValidator(is_file=True),
        only_files=True,
        mandatory=True,
    ).execute()


def prompt_filetype() -> Type[DictionaryItem]:
    return inquirer.select(
        message="What is the format of the file?",
        choices=[
            Choice(value=TurkrutDictionaryItem, name="turkrut.ru"),
        ],
    ).execute()


def prompt_target_language() -> str:
    return inquirer.select(
        message="Choose language you want to translate to.",
        choices=[
            Choice(value="russian", name="Turkish → Russian"),
            Choice(value="turkish", name="Russian → Turkish")
        ],
    ).execute()


def prompt_shuffle() -> bool:
    return inquirer.select(
        message="What order of questions would you prefer?",
        choices=[
            Choice(value=True, name="Shuffled order"),
            Choice(value=False, name="As it is in the file")
        ],
    ).execute()


def prompt_answer_type() -> str:
    return inquirer.select(
        message="How would you prefer to answer?",
        choices=["Type it in", "Choose from multiple options"],
    ).execute()


def answer_with_prompt(word: DictionaryItem, target_language: str):
    if target_language == "russian":
        correct_translation = word.russian
        response = word.ask_translation_to_russian()
        is_correct = word.check_translation_to_russian(response)
    else:
        correct_translation = word.turkish
        response = word.ask_translation_to_turkish()
        is_correct = word.check_translation_to_turkish(response)
    if is_correct:
        print(
            f"[green]Correct![/green] In the file: [green]{correct_translation}[/green]."
        )
    else:
        print(
            f"[red]Incorrect![/red] In the file: [green]{correct_translation}[/green]."
        )
    return is_correct, word


def answer_with_choice(
    the_word: DictionaryItem,
    dictionary: list[DictionaryItem],
    target_language: str,
    n_choices: int = 4
):
    source_language = "turkish" if target_language == "russian" else "russian"
    other_options = random.sample(dictionary, k=n_choices)
    other_options = [
        word for word in other_options if word is not the_word
    ]
    options = other_options[:n_choices - 1] + [the_word]
    random.shuffle(options)
    i = inquirer.select(
        message=f"Choose correct translation for '{getattr(the_word, source_language)}': ",
        choices=[
            Choice(value=i, name=getattr(word, target_language))
            for i, word in enumerate(options)
        ]
    ).execute()

    choice = options[i]
    if choice is the_word:
        print("[green]Correct![/green]")
    else:
        print(
            f"[red]Incorrect![/red] Correct option was '[green]{getattr(the_word, target_language)}[/green]'"
        )


def translation() -> None:
    """
    Practice translation of words from Turkish to Russian or vice versa.
    """
    dict_item = prompt_filetype()

    filename = prompt_filename()
    dictionary = []
    with open(filename, encoding="utf-8") as f:
        for line in f:
            dictionary.append(dict_item(line))

    shuffle = prompt_shuffle()
    if shuffle:
        random.shuffle(dictionary)

    target_language = prompt_target_language()
    answer_type = prompt_answer_type()
    for word in dictionary:
        if answer_type == "Type it in":
            answer_with_prompt(word, target_language)
        elif answer_type == "Choose from multiple options":
            answer_with_choice(word, dictionary, target_language)


if __name__ == "__main__":
    typer.run(translation)
