from enum import Enum
from string import Template
import os
from typing import Optional
import csv

import typer
from rich import print
from InquirerPy import inquirer
from InquirerPy.base.control import Choice

from languages import Language, PrompterInTheLanguage, prompt_language
from dictionary import Dictionary
from csvdictionaryitem import CSVDictionaryItem
from filepath import prompt_filepath
from parse import inside_parenthesis


class WritingMode(str, Enum):
    append = "append"
    create = "create"
    exit = "exit"
    overwrite = "overwrite"


prompt_text = Template("""Type in the word or words in [green]$language[/green].
All parts outside of parenthesis separated by [yellow]"/"[/yellow] would be considered as valid answers.
Text inside parenthesis would be considered as a hint.
[red]Empty string[/red] to exit immediately.""")


def prompt_if_file_exists() -> WritingMode:
    return inquirer.select(
        message="Such file already exists. Do you want to",
        choices=[
            Choice(
                value=WritingMode.append,
                name="Append to the end (only possible if the file is a CSV dictionary)."
            ),
            Choice(
                value=WritingMode.exit,
                name="Abort the program."
            ),
            Choice(
                value=WritingMode.overwrite,
                name="Overwrite the existing file (possible data loss)."
            )
        ]
    ).execute()


def parse_prompt(s: str) -> tuple[list[str], str]:
    print(s)
    hint = inside_parenthesis(s)
    words = s.replace(f"({hint})", "").strip().split("/")
    if hint == "":
        hint = None
    return words, hint


def prompt_one_language(language: Language) -> Optional[tuple[list[str], str]]:
    print(prompt_text.substitute({"language": language.name}))
    prompter = PrompterInTheLanguage(language)
    return prompter(additional_symbols=",-/()")


def prompt_dictionary_item(language_a: Language, language_b: Language) -> Optional[CSVDictionaryItem]:
    if (words_and_hint := prompt_one_language(language_a)) == "":
        return None
    words_a, hint_a = parse_prompt(words_and_hint)

    if (words_and_hint := prompt_one_language(language_b)) == "":
        return None
    words_b, hint_b = parse_prompt(words_and_hint)

    return CSVDictionaryItem(
        words_a,
        words_b,
        language_a,
        language_b,
        hint_a,
        hint_b
    )


def make_dictionary(
    path: Optional[str] = typer.Argument(
        None, help="Destination path of the dictionary"
    )
) -> None:
    if path is None:
        path = prompt_filepath(
            "Type in destination path: ",
            extension=".csv",
            is_file=False,
            directory=CSVDictionaryItem.default_directory()
        )

    mode = WritingMode.create
    if os.path.isfile(path):
        mode = prompt_if_file_exists()
        if mode == WritingMode.exit:
            raise SystemExit("Aborting the program")

    match mode:
        case WritingMode.create | WritingMode.overwrite:
            la = prompt_language("Choose first language")
            lb = prompt_language("Choose second language")
            dictionary = Dictionary([], la, lb)
        case WritingMode.append:
            dictionary = Dictionary.from_file(path, CSVDictionaryItem)
            la, lb = dictionary.language_a, dictionary.language_b
            print(f"Detected languages are {la} and {lb}")

    while True:
        item = prompt_dictionary_item(la, lb)
        if item is None:
            break
        dictionary.append(item)

    dictionary.print("New dictionary")
    with open(path, mode="w", encoding="utf-8", newline="") as f:
        field_names = [la.name, lb.name, f"{la} hint", f"{lb} hint"]
        writer = csv.DictWriter(f, delimiter=";", fieldnames=field_names)
        writer.writeheader()
        for item in sorted(dictionary):
            writer.writerow({
                la.name: "/".join(item.words_a),
                lb.name: "/".join(item.words_b),
                f"{la} hint": item._hint_a,
                f"{lb} hint": item._hint_b
            })


if __name__ == "__main__":
    typer.run(make_dictionary)
