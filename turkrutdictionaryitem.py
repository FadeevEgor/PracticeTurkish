import re
from typing import Type, Optional, TypeVar
from dataclasses import dataclass

from languages import Language
from dictionary import DictionaryItem, Dictionary
from parse import inside_parenthesis

T = TypeVar("T", bound="TurkrutDictionaryItem")


def extract_words_and_hint(s: str) -> tuple[set[str], str]:
    hint = inside_parenthesis(s)
    words = s.replace(f"{hint}", "").strip()
    words = set(words.split(", "))
    return words, hint


@dataclass
class TurkrutDictionaryItem(DictionaryItem):
    """
    A dictionary item from turkrut.ru.
    The structure: 
    Turkish - Russian\n
    Caveats:
    1) The separator could be a dash of various length.
    2) Might include multiple options for russian translation.
    3) Might include additional info inside parenthesis on both sides.
    """

    _turkish: str
    _russian: str
    _turkish_words: set[str]
    _russian_words: set[str]
    _turkish_hint: Optional[str]
    _russian_hint: Optional[str]

    @property
    def language_a(self) -> Language:
        return Language.turkish

    @property
    def language_b(self) -> Language:
        return Language.russian

    @property
    def query_a(self) -> str:
        return self._turkish

    @property
    def query_b(self) -> str:
        return self._russian

    @property
    def words_a(self) -> set[str]:
        return self._turkish_words

    @property
    def words_b(self) -> set[str]:
        return self._russian_words

    @staticmethod
    def extension() -> str:
        return ".txt"

    @staticmethod
    def default_directory() -> str:
        return "turkrut"

    @classmethod
    def from_line(cls: Type[T], line: str) -> T:
        tk, ru = re.split("-|—|–", line)
        tk, ru = tk.strip(), ru.strip()
        tk_words, tk_hint = extract_words_and_hint(tk)
        ru_words, ru_hint = extract_words_and_hint(ru)
        return cls(tk, ru, tk_words, ru_words, tk_hint, ru_hint)

    @classmethod
    def read_dictionary_from_file(cls: Type[T], path: str) -> tuple[list[T], Language, Language]:
        with open(path, encoding="utf-8") as f:
            return [cls.from_line(line) for line in f], Language.turkish, Language.russian
