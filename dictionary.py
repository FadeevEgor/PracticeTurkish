from abc import ABC, abstractmethod
from typing import Type, TypeVar, Optional
from dataclasses import dataclass
from random import shuffle

from rich import print
from rich.table import Table

from russianinput import prompt_russian
from turkishinput import prompt_turkish
from bot import APIConfiguration, send_to_telegram

DI = TypeVar('DI', bound='DictionaryItem')
D = TypeVar('D', bound='Dictionary')


class DictionaryItem(ABC):
    """
    An ABC for a dictionary item.
    Is used in order to practice translation.
    """

    def ask_translation_to_russian(self) -> str:
        question = f"{self.turkish} ⇨ "
        return prompt_russian(question, additional_symbols=",-")

    def ask_translation_to_turkish(self) -> str:
        question = f"{self.russian} ⇨ "
        return prompt_turkish(question, additional_symbols=",-")

    @property
    @abstractmethod
    def russian(self):
        pass

    @property
    @abstractmethod
    def turkish(self):
        pass

    @staticmethod
    @abstractmethod
    def extension() -> str:
        pass

    @staticmethod
    @abstractmethod
    def default_directory() -> str:
        pass

    @abstractmethod
    def check_translation_to_russian(self, answer: str) -> bool:
        pass

    @abstractmethod
    def check_translation_to_turkish(self, answer: str) -> bool:
        pass

    @classmethod
    @abstractmethod
    def read_dictionary_from_file(cls: Type[DI], path: str) -> list[DI]:
        pass


@dataclass
class Dictionary:
    words: list[DictionaryItem]

    @classmethod
    def from_file(cls: D, path: str, T: Type[DictionaryItem]) -> D:
        return cls(T.read_dictionary_from_file(path))

    def print(self, title: Optional[str] = None) -> None:
        self.sort()
        table = Table(title=title)
        table.add_column("Türkçe", justify="left")
        table.add_column("Русский", justify="right")

        for word in self.words:
            table.add_row(word.turkish, word.russian)

        print(table)

    def sent_to_telegram(self) -> bool:
        self.sort()
        rows = [f"{item.turkish} — {item.russian}" for item in self]
        text = "\n".join(rows)
        config = APIConfiguration.from_config()
        return send_to_telegram(
            config.url,
            config.user_id,
            config.token,
            text
        )

    def sort(self) -> None:
        self.words.sort(key=lambda item: item.turkish)

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
