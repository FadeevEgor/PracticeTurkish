from enum import Enum
from functools import partial
from typing import Type, Optional
import random

from rich import print
import typer
from InquirerPy import inquirer
from InquirerPy.base.control import Choice

from languages import prompt_way_of_translation
from dictionary import Dictionary, DictionaryItem
from turkrutdictionaryitem import TurkrutDictionaryItem
from csvdictionaryitem import CSVDictionaryItem
from filepath import prompt_filepath


class AnswerType(str, Enum):
    typing = "typing"
    choice = "choice"


def prompt_filetype() -> Type[DictionaryItem]:
    return inquirer.select(
        message="What is the format of the file?",
        choices=[
            Choice(value=TurkrutDictionaryItem, name="turkrut.ru"),
            Choice(value=CSVDictionaryItem, name="csv"),
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


def prompt_answer_type() -> AnswerType:
    return inquirer.select(
        message="How would you prefer to answer?",
        choices=[
            Choice(value=AnswerType.typing, name="Type it in"),
            Choice(value=AnswerType.choice, name="Choose from multiple options")
        ],
    ).execute()


def answer_with_prompt(word: DictionaryItem, a2b: bool) -> bool:
    answer = word.ask_translation(a2b)
    is_correct = word.check_translation(a2b, answer)
    correct_translation = word.query_b if a2b else word.query_a
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
    print(f'In the file: "[green]{correct_translation}[/green]"')
    return is_correct, word


def answer_with_choice(
    the_word: DictionaryItem,
    dictionary: Dictionary,
    a2b: bool,
    n_choices: int = 4
) -> tuple[bool, DictionaryItem]:
    query = the_word.query_a if a2b else the_word.query_b
    other_options = random.sample(dictionary.words, k=n_choices)
    other_options = [
        word for word in other_options if word is not the_word
    ]
    options = other_options[:n_choices - 1] + [the_word]
    random.shuffle(options)
    choices = [
        Choice(
            value=i,
            name=word.query_b if a2b else word.query_a
        ) for i, word in enumerate(options)
    ]

    i = inquirer.select(message=f"{query} ⇨ ", choices=choices).execute()

    choice = options[i]
    if choice is the_word:
        print("[green]Correct![/green]")
        return True, the_word
    correct_answer = the_word.query_b if a2b else the_word.query_a
    print(
        f"[red]Incorrect![/red] Correct option was '[green]{correct_answer}[/green]'"
    )
    return False, the_word


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
    """
    Practice translation of words from Turkish to Russian or vice versa.
    If any option is not specified via CLI, it will be prompted later.
    """
    dictionary_item_type = prompt_filetype()

    if path is None:
        path = prompt_filepath(
            message="Choose file to practice: ",
            is_file=True,
            extension=dictionary_item_type.extension(),
            directory=dictionary_item_type.default_directory()
        )
    dictionary = Dictionary.from_file(path, dictionary_item_type)

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
    for word in dictionary:
        is_correct, word = answer_function(word)
        if not is_correct:
            mistakes.append(word)

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
