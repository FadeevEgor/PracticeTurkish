from abc import ABC, abstractmethod
from typing import Type, TypeVar, Optional, Iterator, Generic
from dataclasses import dataclass
from random import shuffle

from rich import print
from rich.table import Table

from practice_turkish.languages import Language, PrompterInTheLanguage
from practice_turkish.dictionaries.telegram import (
    APIConfiguration,
    send_to_telegram,
    TelegramError,
)

DE = TypeVar("DE", bound="DictionaryEntry")
D = TypeVar("D", bound="Dictionary")


class DictionaryFormatError(ValueError):
    """Exception raised if dictionary file violates specification."""


class DictionaryEntry(ABC):
    """An ABC used to represent an entry from a dictionary of an arbitrary format.

    Abstract base class for all classes used to represent entries from dictionaries of
    concrete type.

    Prompting an answer and checking if its correct already implemented
    here. Each subclass should implement all the following properties and methods.

    Properties
    ----------
    language_a : Language
        The 1st language (language A below) of the dictionary.
    language_b : Language
        The 2nd language (language B below) of the dictionary.
    query_a : str
        The query to be showed when prompted to translate from language A to
        language B.
    query_b : str
        The query to be showed when prompted to translate from language B to
        language A.
    words_a : set[str]
        Set of options to be considered correct when prompted to translate from
        language B to language A.
    words_b : set[str]
        Set of options to be considered correct when prompted to translate from
        language A to language B.

    Methods
    ----------
    @classmethod
    def extension(cls) -> str
        Returns the file extension used with dictionary of this format.

    @staticmethod
    def default_directory() -> str
        Returns a string representing the default directory dictionary of this
        format are stored in.

    @classmethod
    def read_dictionary_from_file(cls, path: str) -> Dictionary
        Read the dictionary of entries of the type from a file.
    """

    def prompt_translation(self, a2b: bool) -> str:
        """Prompt the translation for the entry from the user by typing the answer in.

        Parameters
        ----------
        a2b : bool
            True, if translation should be prompted from language A to
            B language. False otherwise.

        Returns
        ----------
        translation : str
            The string typed in by the user.
        """
        query = self.query_a if a2b else self.query_b
        prompter = PrompterInTheLanguage(self.language_b if a2b else self.language_a)
        return prompter.prompt(f"{query} ⇨ ", additional_symbols=",-")

    def check_translation(self, a2b: bool, translation: str) -> bool:
        """Check translation.

        Parameters
        ----------
        a2b : bool
            True, if translation is given in the language B language A to
            B language, False otherwise.
        translation : str
            A string with translation, typically typed in by the user.

        Returns
        ----------
        x : bool
            True, if the translation is correct, False otherwise.
        """
        translation = translation.strip()
        if translation == "":
            return False

        target = self.words_b if a2b else self.words_a
        return translation in target

    def __lt__(self, other: DE) -> bool:
        """Necessary to sort"""
        return self.words_a < other.words_b

    @property
    @abstractmethod
    def language_a(self) -> Language:
        """First language of the entry."""
        raise NotImplementedError

    @property
    @abstractmethod
    def language_b(self) -> Language:
        """Second language of the entry."""
        raise NotImplementedError

    @property
    @abstractmethod
    def query_a(self) -> str:
        """Query to show when prompting translation to language A."""
        raise NotImplementedError

    @property
    @abstractmethod
    def query_b(self) -> str:
        """Query to show when prompting translation to language A."""
        raise NotImplementedError

    @property
    @abstractmethod
    def words_a(self) -> set[str]:
        """Values to be considered correct translation to language A."""
        raise NotImplementedError

    @property
    @abstractmethod
    def words_b(self) -> set[str]:
        """Values to be considered correct translation to language B."""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def extension() -> str:
        """File extension associated with this type of entries."""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def default_directory() -> str:
        """Directory name associated with this type of entries."""
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def read_dictionary_from_file(
        cls: Type[DE], path: str
    ) -> tuple[list[DE], Language, Language]:
        """Read list entries of this type from a file."""
        raise NotImplementedError


@dataclass
class Dictionary(Generic[DE]):
    """A class used to represent a dictionary.

    A dictionary is a list of homogeneous dictionary entries. Instances of the
    class are used in order to run translation sessions. Contains list of
    DictionaryEntry instances, and delegates iteration and indexation to the
    list.

    Attributes
    ----------
    entries : list[DictionaryEntry]
        List of entries.
    language_a : Language
        Language A of the dictionary.
    language_b : Language
        Language B of the dictionary.

    Methods
    ----------
    @classmethod
    def from_file(cls, path: str, T: Type[DictionaryEntry]) -> Dictionary:
        Reads dictionary form a file assuming the type T.

    def print(self, title: Optional[str] = None) -> None:
        Prints the dictionary to stdout in a from of the table.

    def send_to_telegram(self) -> bool:
        Send the dictionary to a telegram user via the bot.
    """

    entries: list[DE]
    language_a: Language
    language_b: Language

    @classmethod
    def from_file(cls: Type[D], path: str, type: Type[DE]) -> D:
        "Read dictionary form a file assuming the type T."
        return cls(*type.read_dictionary_from_file(path))

    def print(self, title: Optional[str] = None) -> None:
        "Print the dictionary to stdout in a from of the table."
        self.sort()
        table = Table(title=title)
        table.add_column(self.language_a, justify="left")
        table.add_column(self.language_b, justify="right")

        for word in self.entries:
            table.add_row(word.query_a, word.query_b)

        print(table)

    def send_to_telegram(self, path: str = "config.ini") -> bool:
        """Send the dictionary to a telegram user via the bot.

        Parameters:
        ----------
        path : str
            A string representing a path to a configuration file.
        """
        self.sort()
        rows = [f"{item.query_a} — {item.query_b}" for item in self]
        text = "\n".join(rows)
        try:
            config = APIConfiguration.read_ini(path)
            status = send_to_telegram(config.url, config.user_id, config.token, text)
        except TelegramError as exception:
            exception_type = type(exception).__name__
            print(f"[red]{exception_type}[/red]: [yellow]{exception}[/yellow]")
            return False
        return status

    def sort(self) -> None:
        "Sort the dictionary with respect to the language A."
        self.entries.sort(key=lambda item: item.query_a)

    def insert(self, entry: DE) -> None:
        "Insert a new entry."
        self.entries.append(entry)

    def shuffle(self) -> None:
        "Shuffle entries."
        shuffle(self.entries)

    def __iter__(self) -> Iterator[DE]:
        return iter(self.entries)

    def __len__(self) -> int:
        return len(self.entries)

    def __getitem__(self, index: int) -> DE:
        return self.entries[index]
