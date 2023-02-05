import os
from pathlib import Path
from typing import Generator, Optional

from InquirerPy import inquirer
from prompt_toolkit.document import Document
from prompt_toolkit.completion import Completion, CompleteEvent
from InquirerPy.prompts.filepath import FilePathCompleter
from InquirerPy.validator import PathValidator


class ExtensionFilePathCompleter(FilePathCompleter):
    """
    Modifies behaviour of FilePathCompleter to filter completions by extension
    """

    def __init__(
        self,
        only_directories: bool = False,
        only_files: bool = False,
        extension: Optional[str] = None
    ):
        super().__init__(only_directories, only_files)
        self.extension = extension

    def get_completions(
        self,
        document: Document,
        complete_event: CompleteEvent
    ) -> Generator[Completion, None, None]:
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
    validator = PathValidator(is_file=True) if is_file else None
    completer = ExtensionFilePathCompleter(extension=extension)
    directory = Path(directory) if directory is not None else Path.cwd()

    return inquirer.text(
        message=message,
        default=str(directory.absolute()) + os.path.sep,
        completer=completer,
        validate=validator
    ).execute()


if __name__ == "__main__":
    print(prompt_filepath("> ", extension=".txt", is_file=True))
