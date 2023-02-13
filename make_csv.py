import os
from typing import Optional
import csv


import typer
from rich import print
from InquirerPy import inquirer
from InquirerPy.base.control import Choice

from turkishinput import prompt_turkish
from russianinput import prompt_russian
from dictionary import Dictionary
from csvdictionaryitem import CSVDictionaryItem
from filepath import prompt_filepath
from parse import inside_parenthesis


def prompt_if_file_exists() -> str:
    return inquirer.select(
        message="Such file already exists. Do you want to",
        choices=[
            Choice(
                value="append",
                name="Append to the end (only possible if the file is a CSV dictionary)."
            ),
            Choice(value="exit", name="Abort the program."),
            Choice(value="write",
                   name="Overwrite the existing file (possible data loss).")
        ]
    ).execute()


def parse_prompt(s: str) -> tuple[list[str], str]:
    hint = inside_parenthesis(s)
    words = s.replace(f"({hint})", "").strip().split("/")
    if hint == "":
        hint = None
    return words, hint


def prompt_item() -> Optional[CSVDictionaryItem]:
    print("""Type in the word or words in [green]turkish[/green].
All words outside of parenthesis separated by [yellow]"/"[/yellow] would be considered a valid answers.
Text inside parenthesis would be considered as a hint.
[red]Empty string[/red] to exit immediately.""")

    if (turkish_prompt := prompt_turkish(additional_symbols=",-/()")) == "":
        return None
    turkish_words, turkish_hint = parse_prompt(turkish_prompt)

    print("""Type in [green]russian[/green] word or words.
All words outside of parenthesis separated by [yellow]"/"[/yellow] would be considered valid answers.
Text inside parenthesis would be considered as a hint.
[red]Empty string[/red] to exit immediately.""")
    if (russian_prompt := prompt_russian(additional_symbols=",-/()")) == "":
        return None
    russian_words, russian_hint = parse_prompt(russian_prompt)

    return CSVDictionaryItem(
        russian_words,
        turkish_words,
        russian_hint,
        turkish_hint
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

    mode = "write"
    if os.path.isfile(path):
        mode = prompt_if_file_exists()
        if mode == "exit":
            raise SystemExit("Aborting the program")

    dictionary: list[CSVDictionaryItem] = []
    while True:
        item = prompt_item()
        if item is None:
            break
        dictionary.append(item)

    if mode == "append":
        dictionary = CSVDictionaryItem.read_dictionary_from_file(
            path
        ) + dictionary

    Dictionary(dictionary).print("New dictionary")
    with open(path, mode="w", encoding="utf-8", newline="") as f:
        field_names = ["turkish", "russian", "turkish hint", "russian hint"]
        writer = csv.DictWriter(f, delimiter=";", fieldnames=field_names)
        writer.writeheader()
        for item in sorted(dictionary):
            writer.writerow({
                "turkish": "/".join(item.turkish_words),
                "russian": "/".join(item.russian_words),
                "turkish hint": item.turkish_hint,
                "russian hint": item.russian_hint
            })


if __name__ == "__main__":
    typer.run(make_dictionary)
