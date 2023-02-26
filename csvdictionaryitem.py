from typing import Optional, Type, TypeVar
from dataclasses import dataclass, asdict
import csv

from languages import Language
from dictionary import DictionaryItem, DictionaryFormatError

DI = TypeVar("DI", bound="CSVDictionaryItem")


def generate_query(words: list[str], hint: Optional[str]) -> str:
    query = "/".join(words)
    if hint is not None:
        query += f" ({hint})"
    return query


def parse_language(language: str) -> Language:
    normalized = language.strip().lower()
    try:
        return Language[normalized]
    except KeyError:
        raise DictionaryFormatError(f"Not supported language {language}.")


def parse_header(header: list[str]) -> tuple[Language, Language]:
    if len(header) != 4:
        raise DictionaryFormatError(
            "Incorrect number of columns in the CSV file."
        )
    lang_a_header, lang_b_header, _, _ = header
    return parse_language(lang_a_header), parse_language(lang_b_header)


@dataclass
class CSVDictionaryItem(DictionaryItem):
    _words_a: list[str]
    _words_b: list[str]
    _language_a: Language
    _language_b: Language
    _hint_a: Optional[str] = None
    _hint_b: Optional[str] = None

    @property
    def language_a(self) -> Language:
        return self._language_a

    @property
    def language_b(self) -> Language:
        return self._language_b

    @property
    def words_a(self) -> set[str]:
        return set(self._words_a)

    @property
    def words_b(self) -> set[str]:
        return set(self._words_b)

    @property
    def query_a(self) -> str:
        return generate_query(self.words_a, self._hint_a)

    @property
    def query_b(self) -> str:
        return generate_query(self.words_b, self._hint_b)

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

    @classmethod
    def read_dictionary_from_file(cls: Type[DI], path: str) -> tuple[list[DI], Language, Language]:
        with open(path,  encoding="utf-8") as f:
            reader = csv.reader(f, delimiter=";")
            header = next(reader)
            language_a, language_b = parse_header(header)

            dictionary: list[DI] = []
            for words_a, words_b, hint_a, hint_b in reader:
                words_a = words_a.split("/")
                words_b = words_b.split("/")
                hint_a = None if not hint_a else hint_a
                hint_b = None if not hint_b else hint_b
                dictionary.append(
                    cls(
                        words_a,
                        words_b,
                        language_a,
                        language_b,
                        hint_a,
                        hint_b
                    )
                )

            return dictionary, language_a, language_b

    def __lt__(self, other: DI) -> bool:
        return self.words_a < other.words_b


if __name__ == "__main__":
    import os
    from dictionary import Dictionary

    path = os.path.join("CSV", "test.csv")
    dictionary = Dictionary(
        CSVDictionaryItem.read_dictionary_from_file(path)
    )
    dictionary.print()
