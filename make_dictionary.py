import os
from enum import Enum
from typing import Optional
import json

import typer
from rich import print
from InquirerPy import inquirer
from InquirerPy.base.control import Choice

from turkishinput import prompt_turkish
from russianinput import prompt_russian
from jsondictionaryitem import JSONDictionaryItem
from filepath import prompt_filepath


def prompt_if_file_exists() -> str:
    return inquirer.select(
        message="Such file already exists. Do you want to",
        choices=[
            Choice(
                value="append",
                name="Append to the end (only possible if the file is a JSON dictionary)."
            ),
            Choice(value="exit", name="Abort the program."),
            Choice(value="write",
                   name="Overwrite the existing file (possible data loss).")
        ]
    ).execute()


def make_dictionary(
    path: Optional[str] = typer.Argument(
        None, help="Destination path of the dictionary"
    )
) -> None:
    if path is None:
        path = prompt_filepath(
            "Type in destination path: ",
            extension=".json",
            is_file=False
        )

    mode = "write"
    if os.path.isfile(path):
        mode = prompt_if_file_exists()
        if mode == "exit":
            raise SystemExit("Aborting the program")

    dictionary: list[JSONDictionaryItem] = []
    while True:
        print("""Type in [green]turkish[/green] word or words.
Use [yellow]", "[/yellow] as separator in the case of several words.
[red]Empty string[/red] to exit immediately.""")
        turkish_words = prompt_turkish(allow_coma=True)
        if turkish_words == "":
            break
        print("""Type in [green]russian[/green] word or words.
Use [yellow]", "[/yellow] as separator in the case of several words.
[red]Empty string[/red] to exit immediately.""")
        russian_words = prompt_russian(allow_coma=True)
        if russian_words == "":
            break
        print("""Type in a hint in [green]turkish[/green].
Empty string for no-hint.""")
        turkish_hint = prompt_turkish()
        print("""Type in a hint in [green]russian[/green].
Empty string for no-hint.""")
        russian_hint = prompt_russian()

        dictionary.append(
            JSONDictionaryItem(
                turkish_words=turkish_words.split(", "),
                russian_words=russian_words.split(", "),
                russian_hint=russian_hint if russian_hint != "" else None,
                turkish_hint=turkish_hint if turkish_hint != "" else None,
            )
        )

    dictionary = [item.to_dict() for item in dictionary]
    if mode == "append":
        with open(path, mode="r", encoding="utf-8") as f:
            dictionary = json.load(f) + dictionary

    with open(path, mode="w", encoding="utf-8") as f:
        json.dump(
            dictionary,
            f,
            ensure_ascii=False,
            indent=4
        )


if __name__ == "__main__":
    typer.run(make_dictionary)
