import os
from pathlib import Path
from typing import Generator, Optional, Type

from prompt_toolkit.document import Document
from prompt_toolkit.completion import Completion, CompleteEvent
from InquirerPy import inquirer
from InquirerPy.prompts.filepath import FilePathCompleter
from InquirerPy.validator import PathValidator
from InquirerPy.base.control import Choice

from practice_turkish.dictionaries import (
    DictionaryEntry,
    CSVDictionaryEntry,
    TurkrutDictionaryEntry,
)


class ExtensionFilePathCompleter(FilePathCompleter):
    """A class used to generate completions for path of a file with an extension.

    Extends `FilePathCompleter` provided by `InquirerPy` library. Overloads the
    `get_completions` method to generate completions only for files with
    specified extension, given the extension is provided.

    Attributes
    ----------
    only_directories : bool
        True, if completions should contain only directories, False by default
    only_files : bool
        True, if completions should contain only directories, False by default.
    extension : Optional[str]
        If given, all files with extensions differing from specified will be
        filtered from completions. By default (None) no filtering is performed.
    """

    def __init__(
        self,
        only_directories: bool = False,
        only_files: bool = False,
        extension: Optional[str] = None,
    ):
        super().__init__(only_directories, only_files)
        self.extension = extension

    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> Generator[Completion, None, None]:
        "Generator yielding possible path completions."
        all_valid_path_completions = list(
            super().get_completions(document, complete_event)
        )
        for completion in all_valid_path_completions:
            filename = completion.text
            if filename.startswith("."):
                continue
            path = Path(document.current_line, filename)
            if self.extension is not None:
                if path.is_file() and path.suffix != self.extension:
                    continue
            yield completion


def prompt_filepath(
    message: str,
    is_file: bool = False,
    extension: Optional[str] = None,
    directory: Optional[str] = None,
) -> str:
    """Prompt a file path from the user.

    Parameters
    ----------
    message : str
        A text to be printed before the prompt.
    is_file : bool
        True, if the path should lead to an existing file.
    extension : Optional[str]
        The extension of the filepath to be prompted.
    directory : Optional[str]
        A string representing a path to a directory, inside of which the path
        should lead to.

    Returns
    ----------
    path : str
        A string representing a path to a file.
    """
    validator = PathValidator(is_file=True) if is_file else None
    completer = ExtensionFilePathCompleter(extension=extension)
    path = Path(directory) if directory is not None else Path.cwd()
    return inquirer.text(
        message=message,
        default=str(path.absolute()) + os.path.sep,
        completer=completer,
        validate=validator,
    ).execute()


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


if __name__ == "__main__":
    print(prompt_filepath("> ", extension=".txt", is_file=True))
