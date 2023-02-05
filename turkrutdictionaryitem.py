import re
from typing import Type, Optional, TypeVar, ClassVar
from dataclasses import dataclass

from dictionary import DictionaryItem
from parse import inside_parenthesis

T = TypeVar("T", bound="TurkrutDictionaryItem")


@dataclass
class TurkrutDictionaryItem(DictionaryItem):
    """
    A dictionary item from turkrut.ru.
    The structure: 
    Turkish - Russian\n
    Caveats:
    1) The separator could be a dash of various length.
    2) Might include multiple options for russian translation.
    3) Might include include additional info inside parenthesis on both sides.
    """

    russian: str
    turkish: str
    russian_words: set[str]
    turkish_word: str
    russian_hint: Optional[str]
    turkish_hint: Optional[str]

    @staticmethod
    def extension() -> str:
        return ".txt"

    @staticmethod
    def default_directory() -> str:
        return "turkrut"

    def check_translation_to_russian(self, answer: str) -> bool:
        answer = answer.strip()
        if answer == "":
            return False
        return answer in self.russian_words | {self.russian_hint}

    def check_translation_to_turkish(self, answer: str) -> bool:
        answer = answer.strip()
        if answer == "":
            return False
        return answer in {self.turkish_word, self.turkish_hint}

    @classmethod
    def from_line(cls: Type[T], line: str) -> T:
        turkish, russian = re.split("-|—|–", line)
        turkish, russian = turkish.strip(), russian.strip()
        turkish_hint = inside_parenthesis(turkish)
        russian_hint = inside_parenthesis(russian)
        turkish_word = turkish.replace(
            f"({turkish_hint})", ""
        ).strip()
        russian_words = russian.replace(
            f"({russian_hint})", ""
        ).strip()
        russian_words = set(russian_words.split(", "))
        return cls(
            russian,
            turkish,
            russian_words,
            turkish_word,
            russian_hint,
            turkish_hint
        )

    @classmethod
    def read_dictionary_from_file(cls: Type[T], path: str) -> list[T]:
        with open(path, encoding="utf-8") as f:
            return [cls.from_line(line) for line in f]
