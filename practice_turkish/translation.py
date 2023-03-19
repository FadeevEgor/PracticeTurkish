from enum import Enum, auto
from functools import partial
from typing import Type, Optional
import random

from rich import print
import typer
from InquirerPy import inquirer
from InquirerPy.base.control import Choice

from dictionary import Dictionary, DictionaryEntry
from languages import prompt_way_of_translation
from turkrutdictionary import TurkrutDictionaryEntry
from csvdictionary import CSVDictionaryEntry
from filepath import prompt_filepath


class AnswerType(str, Enum):
    """An enum used to represent form of the answers by an user.

    Values
    ----------
    typing
        User types in an answer using a keyboard.
    choice
        User picks an answer from a list of options.
    """
    typing = auto()
    choice = auto()


def prompt_dictionary_type() -> Type[DictionaryEntry]:
    """Prompt a type of a dictionary from the user.

    Request the user to pick a type of a supported dictionary. 
    This type later is used in order to parse the content of the file.

    Returns
    ----------
    T : A subclass of DictionaryItem class
    """
    return inquirer.select(
        message="What is the format of the file?",
        choices=[
            Choice(value=TurkrutDictionaryEntry, name="turkrut.ru"),
            Choice(value=CSVDictionaryEntry, name="csv"),
        ],
    ).execute()


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
            Choice(value=False, name="As it is in the file")
        ],
    ).execute()


def prompt_answer_type() -> AnswerType:
    "Prompt the user to pick the form of their answers."
    return inquirer.select(
        message="How would you prefer to answer?",
        choices=[
            Choice(value=AnswerType.typing, name="Type it in"),
            Choice(value=AnswerType.choice, name="Choose from multiple options")
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
        print(
            f"[green]Correct![/green]",
            end=" "
        )
    else:
        print(
            f"[red]Incorrect![/red]",
            end=" "
        )
    print(f'In the file: "[green]{correct_translation}[/green]".')
    return is_correct


def answer_with_choice(
    the_entry: DictionaryEntry,
    dictionary: Dictionary,
    a2b: bool,
    n_choices: int = 4
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
        entry for entry in incorrect_options if entry is not the_entry
    ]
    options = [the_entry] + incorrect_options[:n_choices - 1]
    random.shuffle(options)
    choices = [
        Choice(
            value=i,
            name=o.query_b if a2b else o.query_a
        ) for i, o in enumerate(options)
    ]

    i = inquirer.select(message=f"{query} ⇨ ", choices=choices).execute()

    choice = options[i]
    if choice is the_entry:
        print("[green]Correct![/green]")
        return True
    correct_answer = the_entry.query_b if a2b else the_entry.query_a
    print(
        f"[red]Incorrect![/red] Correct option was '[green]{correct_answer}[/green]'"
    )
    return False


def translation(
    path: Optional[str] = typer.Option(
        None, "--path", help="Path to an exercise file."
    ),
    shuffle: Optional[bool] = typer.Option(
        None, "--shuffle", help="Whether to shuffle entries in the exercise or not"
    ),
    answer_type: Optional[AnswerType] = typer.Option(
        None, "--answer", help="Whether to answer by typing it in or by choosing it from multiple options"
    )
) -> None:
    """Run a translation session based on a dictionary.

    1) Load the dictionary based on a given path (prompted if `path` is None);
    2) Prompt the user to translate each entry in the dictionary, possibly in 
    a shuffled order (prompted if `shuffle` is None);
    3) Show summary of the session, and sends mistakes to telegram.   

    Parameters
    ----------
    path : Optional[str]
        A string representing path to the dictionary file, or None (default)
        if it is to be prompted within session.
    shuffle : Optional[bool]
        True, if the dictionary is to be shuffled. 
        False, if the order of entries in the dictionary to be kept.
        None (default), if whether to shuffle the dictionary or note to be
        prompted.
    answer_type: Optional[AnswerType]
        Form of the answers by an user. An enum with following values. 
        AnswerType.typing, if the answer is to be typed in.
        AnswerType.choice, if the answer is to be chosen for a list of 
        options.
        None (default), if it is to be prompted.
    """
    dictionary_entry_type = prompt_dictionary_type()

    if path is None:
        path = prompt_filepath(
            message="Choose file to practice: ",
            is_file=True,
            extension=dictionary_entry_type.extension(),
            directory=dictionary_entry_type.default_directory()
        )
    dictionary = Dictionary.from_file(path, dictionary_entry_type)

    if shuffle is None:
        shuffle = prompt_shuffle()
    if shuffle:
        dictionary.shuffle()

    a2b = prompt_way_of_translation(
        dictionary.language_a, dictionary.language_b
    )
    if answer_type is None:
        answer_type = prompt_answer_type()

    match answer_type:
        case AnswerType.typing:
            answer_function = partial(
                answer_with_prompt, a2b=a2b
            )
        case AnswerType.choice:
            answer_function = partial(
                answer_with_choice,
                a2b=a2b,
                dictionary=dictionary
            )

    mistakes = Dictionary([], dictionary.language_a, dictionary.language_b)
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
    if inquirer.confirm(message="Send your mistakes to telegram", default=True).execute():
        mistakes.send_to_telegram()


if __name__ == "__main__":
    typer.run(translation)
