import re

from dictionaryitem import DictionaryItem


def inside_parenthesis(s: str):
    """
    Extracts a part of the string s between parenthesis.
    Useful to extract alternate translation or hint in the format.
    """
    try:
        return re.search(r"\(.+\)", s).group()[1:-1]
    except AttributeError:
        return ""


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

    def __init__(self, line: str):
        turkish, russian = re.split("-|—|–", line)
        self.turkish, self.russian = turkish.strip(), russian.strip()
        self.turkish_hint = inside_parenthesis(self.turkish)
        self.russian_hint = inside_parenthesis(self.russian)
        self.turkish_word = self.turkish.replace(
            f"({self.turkish_hint})", ""
        ).strip()
        self.russian_words = self.russian.replace(
            f"({self.russian_hint})", ""
        ).strip()
        self.russian_words = set(self.russian_words.split(", "))

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
