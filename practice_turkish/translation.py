from enum import Enum
from functools import partial
from typing import Type, Callable
import random

from rich import print
import typer
from InquirerPy import inquirer
from InquirerPy.base.control import Choice

from practice_turkish.languages import prompt_way_of_translation
from practice_turkish.filepath import prompt_filepath, prompt_dictionary_type
from practice_turkish.dictionaries import (
    Dictionary,
    DictionaryEntry,
)


class AnswerType(str, Enum):
    """An enum used to represent form of the answers by an user.

    Values
    ----------
    typing
        User types in an answer using a keyboard.
    choice
        User picks an answer from a list of options.
    """

    TYPING = "TYPING"
    CHOICE = "CHOICE"


def prompt_shuffle() -> bool:
    """Prompt the user whether to shuffle the dictionary or not.

    Returns
    ----------
    x : bool
        True if user chooses to shuffle, False otherwise.
    """
    return inquirer.select(
        message="What order of questions would you prefer?",
        choices=[
            Choice(value=True, name="Shuffled order"),
            Choice(value=False, name="As it is in the file"),
        ],
    ).execute()


def prompt_answer_type() -> AnswerType:
    "Prompt the user to pick the form of their answers."
    return inquirer.select(
        message="How would you prefer to answer?",
        choices=[
            Choice(value=AnswerType.TYPING, name="Type it in"),
            Choice(value=AnswerType.CHOICE,
                   name="Choose from multiple options"),
        ],
    ).execute()


def answer_with_prompt(entry: DictionaryEntry, a2b: bool) -> bool:
    """Prompt an answer from the user by typing it in, and check its correctness.

    Prompt the user to translate a dictionary item by typing a translation
    in console, and check if the translation is correct.

    Parameters
    ----------
    entry : DictionaryEntry
        The dictionary entry to be practiced.
    a2b : bool
        True, if translation should be checked from language a to language b.
        False, otherwise.

    Returns
    ----------
    is_correct : bool
        True if translation is correct, False otherwise.
    """
    answer = entry.prompt_translation(a2b)
    is_correct = entry.check_translation(a2b, answer)
    correct_translation = entry.query_b if a2b else entry.query_a
    if is_correct:
        print("[green]Correct![/green]", end=" ")
    else:
        print("[red]Incorrect![/red]", end=" ")
    print(f'In the file: "[green]{correct_translation}[/green]".')
    return is_correct


def answer_with_choice(
    the_entry: DictionaryEntry,
    dictionary: Dictionary[DictionaryEntry],
    a2b: bool,
    n_choices: int = 4,
) -> bool:
    """Prompt an answer from the user by picking from several options, check its correctness.

    Prompt the user to translate a dictionary item by picking an answer from
    list of `n_choices` options, and check if the user picked the correct one.

    Parameters
    ----------
    the_entry : DictionaryEntry
        The dictionary entry to be practiced.
    dictionary : Dictionary
        The dictionary other options will be sampled from.
    a2b : bool
        True, if translation should be checked from language a to language b.
        False, otherwise.
    n_choices : int
        The number of options to pick from, default is 4.

    Returns
    ----------
    is_correct : bool
        True if translation is correct, False otherwise.
    """
    query = the_entry.query_a if a2b else the_entry.query_b
    incorrect_options = random.sample(dictionary.entries, k=n_choices)
    incorrect_options = [
        entry for entry in incorrect_options if entry is not the_entry]
    options = [the_entry] + incorrect_options[: n_choices - 1]
    random.shuffle(options)
    choices = [
        Choice(value=i, name=o.query_b if a2b else o.query_a)
        for i, o in enumerate(options)
    ]

    i = inquirer.select(message=f"{query} ⇨ ", choices=choices).execute()

    choice = options[i]
    if choice is the_entry:
        print("[green]Correct![/green]")
        return True
    correct_answer = the_entry.query_b if a2b else the_entry.query_a
    print(
        f"[red]Incorrect![/red] Correct option was '[green]{correct_answer}[/green]'")
    return False


def prepare_session() -> (
    tuple[Dictionary[DictionaryEntry], Callable[[DictionaryEntry], bool]]
):
    """Prepare translation session.

    1) Prompts dictionary type, path to it and then loads it.
    2) Prompts form of answering, and prepares answer function

    Returns
    ----------
    dictionary: Dictionary
        Loaded dictionary.
    answer_function: Callable[[DictionaryEntry], bool]
        Function taking in a dictionary entry, prompting user to translate it
        and returning boolean value indicating if the given translation is
        correct.
    """
    dictionary_entry_type = prompt_dictionary_type()
    path = prompt_filepath(
        message="Choose file to practice: ",
        is_file=True,
        extension=dictionary_entry_type.extension(),
        directory=dictionary_entry_type.default_directory(),
    )
    dictionary = Dictionary.from_file(path, dictionary_entry_type)
    if prompt_shuffle():
        dictionary.shuffle()

    a2b = prompt_way_of_translation(
        dictionary.language_a, dictionary.language_b)
    match prompt_answer_type():
        case AnswerType.TYPING:
            answer_function = partial(answer_with_prompt, a2b=a2b)
        case AnswerType.CHOICE:
            answer_function = partial(
                answer_with_choice, a2b=a2b, dictionary=dictionary
            )

    return dictionary, answer_function


def translation(
    config: str = typer.Option(
        "config.ini", "--config", help="Path to your configuration file."
    )
) -> None:
    """Run a translation session based on a dictionary.

    Parameters
    ----------
    config : str
        A string representing path to your configuration file, default is
        'config.ini'.
    """
    dictionary, answer_function = prepare_session()
    mistakes: Dictionary[DictionaryEntry] = Dictionary(
        [], dictionary.language_a, dictionary.language_b
    )
    for entry in dictionary:
        is_correct = answer_function(entry)
        if not is_correct:
            mistakes.insert(entry)

    mistakes.print(title="Your mistakes")
    total = len(dictionary)
    incorrect = len(mistakes)
    correct = total - incorrect
    print(f"Correct:   [green]{correct:3}[/green]/{total}")
    print(f"Incorrect: [red]{incorrect:3}[/red]/{total}")
    if mistakes:
        if inquirer.confirm(
            message="Send your mistakes to telegram", default=True
        ).execute():
            mistakes.send_to_telegram(config)


def main() -> None:
    """If open as a script, run make translate function."""
    typer.run(translation)


if __name__ == "__main__":
    main()
