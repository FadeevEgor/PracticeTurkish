from enum import Enum
from string import Template
import os
from typing import Optional, TypeAlias
import csv

import typer
from rich import print
from InquirerPy import inquirer
from InquirerPy.base.control import Choice

from practice_turkish.languages import Language, PrompterInTheLanguage, prompt_language
from practice_turkish.dictionaries import Dictionary, CSVDictionaryEntry
from practice_turkish.filepath import prompt_filepath
from practice_turkish.dictionaries.parse import inside_parenthesis


CSVDict: TypeAlias = Dictionary[CSVDictionaryEntry]


class WritingMode(str, Enum):
    """Enum used to represent writing mode."""

    EXTEND = "EXTEND"
    CREATE = "CREATE"
    EXIT = "EXIT"
    OVERWRITE = "OVERWRITE"


prompt_text = Template(
    """Type in the word or words in [green]$language[/green].
Text inside parenthesis would be considered as a hint.
Other values separated by [yellow]"/"[/yellow] would be considered as valid answers.
[red]Empty string[/red] to exit immediately."""
)


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
                value=WritingMode.EXTEND,
                name="Extend. Only possible if the file is a CSV dictionary.",
            ),
            Choice(value=WritingMode.EXIT, name="Abort the program. No data loss."),
            Choice(
                value=WritingMode.OVERWRITE,
                name="Overwrite the existing file. Possible data loss.",
            ),
        ],
    ).execute()


def prepare_session(path: Optional[str]) -> tuple[CSVDict, str]:
    """Prepares completion session for creating a CSV dictionary.

    Prompts path if not given. Then depending on existence of dictionary there and
    users choice either creates new file, extends existing dictionary, rewrites it,
    or aborts the process.

    Parameters
    ----------
    path : Optional[str]
        A string representing path new dictionary to write to. Will be prompted
        from user, if not given.

    Returns
    ----------
    dictionary : Dictionary[CSVDictionaryEntry]
        Loaded existing dictionary or a new empty dictionary.
    path : str
        A string representing path new dictionary to write to.
    """
    if path is None:
        path = prompt_filepath(
            "Type in destination path: ",
            extension=".csv",
            is_file=False,
            directory=CSVDictionaryEntry.default_directory(),
        )

    mode = WritingMode.CREATE
    if os.path.isfile(path):
        mode = prompt_if_file_exists()
        if mode == WritingMode.EXIT:
            raise SystemExit("Aborting the program")

    match mode:
        case WritingMode.CREATE | WritingMode.OVERWRITE:
            la = prompt_language("Choose first language.")
            lb = prompt_language("Choose second language.")
            dictionary: CSVDict = Dictionary([], la, lb)
        case WritingMode.EXTEND:
            dictionary = Dictionary.from_file(path, CSVDictionaryEntry)
            la, lb = dictionary.language_a, dictionary.language_b
            print(
                f"Detected languages are [green]{la}[/green] and [green]{lb}[/green].\n"
            )
    return dictionary, path


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
    return words, hint if hint else None


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


def prompt_dictionary_entry(
    language_a: Language, language_b: Language
) -> Optional[CSVDictionaryEntry]:
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

    return CSVDictionaryEntry(words_a, words_b, language_a, language_b, hint_a, hint_b)


def prompt_dictionary(dictionary: CSVDict) -> None:
    """Prompts user to type in all dictionary entries.

    Parameters
    ----------
    dictionary: Dictionary[CSVDictionaryEntry]
        A dictionary to fill in with entries.
    """
    while True:
        entry = prompt_dictionary_entry(dictionary.language_a, dictionary.language_b)
        if entry is None:
            return
        dictionary.insert(entry)


def write_dictionary(dictionary: CSVDict, path: str) -> None:
    """Write dictionary to a CSV file.

    Parameters
    ----------
    dictionary : Dictionary[CSVDictionaryEntry]
        Dictionary to write.
    path : str
        A string representing filepath to write to.
    """
    la, lb = dictionary.language_a, dictionary.language_b
    with open(path, mode="w", encoding="utf-8", newline="") as f:
        field_names = [la.name, lb.name, f"{la} hint", f"{lb} hint"]
        writer = csv.DictWriter(f, delimiter=";", fieldnames=field_names)
        writer.writeheader()
        for item in sorted(dictionary):
            writer.writerow(
                {
                    la.name: "/".join(item.words_a),
                    lb.name: "/".join(item.words_b),
                    f"{la} hint": item._hint_a,
                    f"{lb} hint": item._hint_b,
                }
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
    dictionary, path = prepare_session(path)
    prompt_dictionary(dictionary)
    dictionary.print("New dictionary")
    write_dictionary(dictionary, path)


def main() -> None:
    """If open as a script, run make dictionary function."""
    typer.run(make_dictionary)


if __name__ == "__main__":
    main()
