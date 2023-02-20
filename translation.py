from enum import Enum
from functools import partial
from typing import Type, Optional
import random

from rich import print
import typer
from InquirerPy import inquirer
from InquirerPy.base.control import Choice

from dictionary import Dictionary, DictionaryItem
from turkrutdictionaryitem import TurkrutDictionaryItem
from csvdictionaryitem import CSVDictionaryItem
from filepath import prompt_filepath


class Language(str, Enum):
    turkish = "turkish"
    russian = "russian"


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


def prompt_target_language() -> Language:
    return inquirer.select(
        message="Choose language you want to translate to.",
        choices=[
            Choice(value=Language.turkish, name="Russian → Turkish"),
            Choice(value=Language.russian, name="Turkish → Russian"),
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


def answer_with_prompt(word: DictionaryItem, target_language: Language) -> bool:
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
            f"[green]Correct![/green]",
            end=" "
        )
    else:
        print(
            f"[red]Incorrect![/red]",
            end=" "
        )
    print(f"In the file: [green]{correct_translation}[/green].")
    return is_correct, word


def answer_with_choice(
    the_word: DictionaryItem,
    dictionary: Dictionary,
    target_language: Language,
    n_choices: int = 4
) -> tuple[bool, DictionaryItem]:
    source_language = Language.turkish if target_language == "russian" else Language.russian
    other_options = random.sample(dictionary.words, k=n_choices)
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
        return True, the_word
    print(
        f"[red]Incorrect![/red] Correct option was '[green]{getattr(the_word, target_language)}[/green]'"
    )
    return False, the_word


def translation(
    path: Optional[str] = typer.Option(
        None, "--path", help="Path to an exercise file."
    ),
    shuffle: Optional[bool] = typer.Option(
        None, "--shuffle", help="Whether to shuffle entries in the exercise or not"
    ),
    target_language: Optional[Language] = typer.Option(
        None,   "--target", help="Practice translation to"
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

    if target_language is None:
        target_language = prompt_target_language()
    if answer_type is None:
        answer_type = prompt_answer_type()

    match answer_type:
        case AnswerType.typing:
            answer_function = partial(
                answer_with_prompt, target_language=target_language
            )
        case AnswerType.choice:
            answer_function = partial(
                answer_with_choice,
                target_language=target_language,
                dictionary=dictionary
            )

    mistakes = Dictionary([])
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
        mistakes.sent_to_telegram()


if __name__ == "__main__":
    typer.run(translation)
