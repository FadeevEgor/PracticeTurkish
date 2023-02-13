from typing import Optional, Type, TypeVar
from dataclasses import dataclass, asdict
import csv

from dictionary import DictionaryItem

DI = TypeVar("DI", bound="CSVDictionaryItem")


@dataclass
class CSVDictionaryItem(DictionaryItem):
    russian_words: list[str]
    turkish_words: list[str]
    russian_hint: Optional[str] = None
    turkish_hint: Optional[str] = None

    @staticmethod
    def extension() -> str:
        return ".csv"

    @staticmethod
    def default_directory() -> str:
        return "CSV"

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> DI:
        return cls(**d)

    @property
    def russian(self):
        russian = "/".join(self.russian_words)
        if self.russian_hint is not None:
            russian += f" ({self.russian_hint})"
        return russian

    @property
    def turkish(self):
        turkish = "/".join(self.turkish_words)
        if self.turkish_hint is not None:
            turkish += f" ({self.turkish_hint})"
        return turkish

    def check_translation_to_russian(self, answer: str) -> bool:
        return answer in self.russian_words

    def check_translation_to_turkish(self, answer: str) -> bool:
        return answer in self.turkish_words

    @classmethod
    def read_dictionary_from_file(cls: Type[DI], path: str) -> list[DI]:
        with open(path,  encoding="utf-8") as f:
            reader = csv.reader(f, delimiter=";")
            header = next(reader)

            dictionary: list[DI] = []
            for tk, ru, tk_hint, ru_hint in reader:
                tk = tk.split("/")
                ru = ru.split("/")
                tk_hint = None if not tk_hint else tk_hint
                ru_hint = None if not ru_hint else ru_hint
                dictionary.append(
                    cls(ru, tk, ru_hint, tk_hint)
                )

            return dictionary

    def __lt__(self, other: DI) -> bool:
        return self.turkish_words < other.turkish_words


if __name__ == "__main__":
    import os
    from dictionary import Dictionary

    path = os.path.join("CSV", "test.csv")
    dictionary = Dictionary(
        CSVDictionaryItem.read_dictionary_from_file(path)
    )
    dictionary.print()
