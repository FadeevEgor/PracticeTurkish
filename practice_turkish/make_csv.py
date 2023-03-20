from enum import Enum
from string import Template
import os
from typing import Optional
import csv

import typer
from rich import print
from InquirerPy import inquirer
from InquirerPy.base.control import Choice

from practice_turkish.languages import Language, PrompterInTheLanguage, prompt_language
from practice_turkish.dictionaries import Dictionary, CSVDictionaryEntry
from practice_turkish.filepath import prompt_filepath
from practice_turkish.dictionaries.parse import inside_parenthesis


class WritingMode(str, Enum):
    extend = "extend"
    create = "create"
    exit = "exit"
    overwrite = "overwrite"


prompt_text = Template("""Type in the word or words in [green]$language[/green].
All parts outside of parenthesis separated by [yellow]"/"[/yellow] would be considered as valid answers.
Text inside parenthesis would be considered as a hint.
[red]Empty string[/red] to exit immediately.""")


def prompt_if_file_exists() -> WritingMode:
    """Prompt the user to choose mode of writing to an existing file.

    Invoked if the user typed in a path leading to an existing file.
    Prompts the user to pick the mode to continue with.
    1) Extend: assuming the path leads to an existing correct CSV dictionary, 
    all new entries are to be inserted in the dictionary and saved to the same
    file. 
    2) Exit: aborts the program immediately. Safe option, existing file is 
    untouched.
    3) Overwrite: ignores the existing file and overwrites its content with 
    entries typed in during following session.

    Returns
    ----------
    mode : WritingMode
        WritingMode.extend, WritingMode.exit or WritingMode.overwrite. 
    """
    return inquirer.select(
        message="Such file already exists. Do you want to",
        choices=[
            Choice(
                value=WritingMode.extend,
                name="Extend. Only possible if the file is a CSV dictionary."
            ),
            Choice(
                value=WritingMode.exit,
                name="Abort the program. No data loss."
            ),
            Choice(
                value=WritingMode.overwrite,
                name="Overwrite the existing file. Possible data loss."
            )
        ]
    ).execute()


def parse_prompt(s: str) -> tuple[list[str], Optional[str]]:
    """Parse a text typed in by the user.

    Parses a piece of text typed in by the user. Expected template is bellow.
    alternative 1/alternative 2/.../alternative n (hint)
    That is, all alternative translations are expected to be separated by the
    splash symbol ("/"), and hint is expected to be inside of parenthesis at
    the end.

    Parameters
    ----------
    s : str
        Text typed in by the user representing entry in one language.

    Returns
    ----------
    words : list[str]
        List of alternative translation for the entry.
    hint : Optional[str]
        A hint or clarification for the entry if given, None otherwise.
    """
    print(s)
    hint = inside_parenthesis(s)
    words = s.replace(f"({hint})", "").strip().split("/")
    if hint == "":
        hint = None
    return words, hint


def prompt_one_language(language: Language) -> str:
    """Prompt the user to type in a part of an entry corresponding to one language. 

    Parameters
    ----------
    language : Language
        The language the prompt should be accepted in. 

    Returns
    ----------
    text : str
        Line of text typed in by the user. Guaranteed to be in the language given
        as first parameter. 
    """
    print(prompt_text.substitute({"language": language.name}))
    prompter = PrompterInTheLanguage(language)
    return prompter.prompt(additional_symbols=",-/()")


def prompt_dictionary_entry(language_a: Language, language_b: Language) -> Optional[CSVDictionaryEntry]:
    """Prompt the user to type in a dictionary entry. 

    Prompts the user to type in a line of text twice. Once for language A,
    and once for language B. If either of the lines typed in by the user
    are empty, None is returned.

    Parameters
    ----------
    language_a : Language
        Language A of the dictionary. 

    language_b : Language
        Language B of the dictionary. 


    Returns
    ----------
    entry : Optional[CSVDictionaryEntry]
        A complete dictionary entry in given two languages if the user typed in
        translation options for both languages, None otherwise.

    """
    if (words_and_hint := prompt_one_language(language_a)) == "":
        return None
    words_a, hint_a = parse_prompt(words_and_hint)

    if (words_and_hint := prompt_one_language(language_b)) == "":
        return None
    words_b, hint_b = parse_prompt(words_and_hint)

    return CSVDictionaryEntry(
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
    """Make a CSV dictionary by prompting the user to type in each entry.

    Creates, extends or overwrites an existing CSV dictionary prompting 
    the user to type in each entry sequentially. An empty entry indicates 
    the end of the dictionary.

    Parameters
    ----------
    path : Optional[str]
        A string representing the filepath, the dictionary is to be written
        to. If None, the filepath is prompted from the user during the 
        session.
    """
    if path is None:
        path = prompt_filepath(
            "Type in destination path: ",
            extension=".csv",
            is_file=False,
            directory=CSVDictionaryEntry.default_directory()
        )

    mode = WritingMode.create
    if os.path.isfile(path):
        mode = prompt_if_file_exists()
        if mode == WritingMode.exit:
            raise SystemExit("Aborting the program")

    match mode:
        case WritingMode.create | WritingMode.overwrite:
            la = prompt_language("Choose first language.")
            lb = prompt_language("Choose second language.")
            dictionary = Dictionary([], la, lb)
        case WritingMode.extend:
            dictionary = Dictionary.from_file(path, CSVDictionaryEntry)
            la, lb = dictionary.language_a, dictionary.language_b
            print(
                f"Detected languages are [green]{la}[/green] and [green]{lb}[/green].\n"
            )

    while True:
        item = prompt_dictionary_entry(la, lb)
        if item is None:
            break
        dictionary.insert(item)

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


def main() -> None:
    typer.run(make_dictionary)


if __name__ == "__main__":
    main()
