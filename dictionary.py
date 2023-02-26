from abc import ABC, abstractmethod
from typing import Type, TypeVar, Optional
from dataclasses import dataclass
from random import shuffle

from rich import print
from rich.table import Table

from languages import Language, PrompterInTheLanguage
from bot import APIConfiguration, send_to_telegram

DI = TypeVar('DI', bound='DictionaryItem')
D = TypeVar('D', bound='Dictionary')


class DictionaryFormatError(ValueError):
    pass


class DictionaryItem(ABC):
    """
    An ABC for a dictionary item.
    Is used in order to practice translation.
    """

    def ask_translation(self, a2b: bool) -> str:
        query = self.query_a if a2b else self.query_b
        prompter = PrompterInTheLanguage(
            self.language_b if a2b else self.language_a
        )
        return prompter(f"{query} ⇨ ", additional_symbols=",-")

    def check_translation(self, a2b: bool, answer: str) -> bool:
        answer = answer.strip()
        if answer == "":
            return False

        target = self.words_b if a2b else self.words_a
        return answer in target

    @property
    def languages(self) -> tuple[Language, Language]:
        return (self.language_a, self.language_b)

    @property
    @abstractmethod
    def language_a(self) -> Language:
        pass

    @property
    @abstractmethod
    def language_b(self) -> Language:
        pass

    @property
    @abstractmethod
    def query_a(self) -> str:
        pass

    @property
    @abstractmethod
    def query_b(self) -> str:
        pass

    @property
    @abstractmethod
    def words_a(self) -> set[str]:
        pass

    @property
    @abstractmethod
    def words_b(self) -> set[str]:
        pass

    @staticmethod
    @abstractmethod
    def extension() -> str:
        pass

    @staticmethod
    @abstractmethod
    def default_directory() -> str:
        pass

    @classmethod
    @abstractmethod
    def read_dictionary_from_file(cls: Type[DI], path: str) -> tuple[list[DI], Language, Language]:
        pass


@dataclass
class Dictionary:
    words: list[DictionaryItem]
    language_a: Language
    language_b: Language

    @classmethod
    def from_file(cls: D, path: str, T: Type[DictionaryItem]) -> D:
        return cls(*T.read_dictionary_from_file(path))

    def print(self, title: Optional[str] = None) -> None:
        self.sort()
        table = Table(title=title)
        table.add_column(self.language_a, justify="left")
        table.add_column(self.language_b, justify="right")

        for word in self.words:
            table.add_row(word.query_a, word.query_b)

        print(table)

    def send_to_telegram(self) -> bool:
        self.sort()
        rows = [
            f"{item.query_a} — {item.query_b}" for item in self
        ]
        text = "\n".join(rows)
        config = APIConfiguration.from_config()
        return send_to_telegram(
            config.url,
            config.user_id,
            config.token,
            text
        )

    def sort(self) -> None:
        self.words.sort(key=lambda item: item.query_a)

    def append(self, word: DictionaryItem) -> None:
        self.words.append(word)

    def shuffle(self) -> None:
        shuffle(self.words)

    def __iter__(self):
        return iter(self.words)

    def __len__(self):
        return len(self.words)

    def __getitem__(self, index: int):
        return self.words[index]
