from typing import Optional, Type, TypeVar, Iterable
from dataclasses import dataclass
import csv

from practice_turkish.languages import Language
from practice_turkish.dictionaries import DictionaryEntry, DictionaryFormatError

DE = TypeVar("DE", bound="CSVDictionaryEntry")


def generate_query(words: Iterable[str], hint: Optional[str]) -> str:
    "Generate query with words separated by '/' and a possible hint."
    query = "/".join(words)
    if hint is not None:
        query += f" ({hint})"
    return query


def parse_language(language: str) -> Language:
    """Parse language from a string and create an instance of Language enum.

    Parameters
    ----------
    language : str
        A string representing a language. Should be equal to one of the values
        of Language enum.

    Raises
    ----------
    DictionaryFormatError
        If the string isn't a value of Language enum.

    """
    normalized = language.strip().lower()
    try:
        return Language[normalized]
    except KeyError:
        raise DictionaryFormatError(f"Not supported language {language}.")


def parse_header(header: list[str]) -> tuple[Language, Language]:
    """Parse languages of the dictionary based on the header of the CSV file.

    Parses languages of the dictionary based on the names of the first two
    columns in the dictionary and returns them in a tuple.

    Parameters
    ----------
    header : list[str]
        A list of column names in a CSV file. Should contain exactly 4 strings.

    Returns
    ----------
    language_a : Language
        Language of the 1st column.
    language_b : Language
        Language of the 2nd column.

    Raises
    ----------
    DictionaryFormatError
        If the number of columns is incorrect or languages can't be parsed.
    """
    if len(header) != 4:
        raise DictionaryFormatError("Incorrect number of columns in the CSV file.")
    lang_a_header, lang_b_header, _, _ = header
    return parse_language(lang_a_header), parse_language(lang_b_header)


@dataclass
class CSVDictionaryEntry(DictionaryEntry):
    """A class used to represent entries of custom dictionary form.

    This form uses a CSV file format with 4 columns to store dictionaries.
    A semicolon (";") is used as the separator of the columns.

    First two columns are mandatory for each entry. They represent correct
    translations from one language to another. Multiple alternative
    translations may be present, in which case they are separated
    by slash ("/") within one cell. Each of the values will be considered
    as a correct translation.

    Other two optional columns may contain possible hints or clarifications
    en each language. They will be shown to the user within a query for
    translation inside parenthesis, but won't be considered as a correct
    translation.

    For meaning of the properties and methods, see its parent ABC.
    """

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

    @classmethod
    def read_dictionary_from_file(
        cls: Type[DE], path: str
    ) -> tuple[list[DE], Language, Language]:
        with open(path, encoding="utf-8") as f:
            reader = csv.reader(f, delimiter=";")
            header = next(reader)
            language_a, language_b = parse_header(header)

            dictionary: list[DE] = []
            for words_a, words_b, hint_a, hint_b in reader:
                dictionary.append(
                    cls(
                        words_a.split("/"),
                        words_b.split("/"),
                        language_a,
                        language_b,
                        None if not hint_a else hint_a,
                        None if not hint_b else hint_b,
                    )
                )
        return dictionary, language_a, language_b
