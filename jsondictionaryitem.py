from typing import Optional, Type, TypeVar
import json
from dataclasses import dataclass, asdict

from dictionary import DictionaryItem

DI = TypeVar("DI", bound="JSONDictionaryItem")


@dataclass
class JSONDictionaryItem(DictionaryItem):
    russian_words: list[str]
    turkish_words: list[str]
    russian_hint: Optional[str] = None
    turkish_hint: Optional[str] = None

    @property
    def extension(self):
        return ".json"

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> DI:
        return cls(**d)

    @property
    def russian(self):
        russian = ", ".join(self.russian_words)
        if self.russian_hint is not None:
            russian += f" ({self.russian_hint})"
        return russian

    @property
    def turkish(self):
        turkish = ", ".join(self.turkish_words)
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
            return [
                cls.from_dict(d) for d in json.load(f)
            ]


if __name__ == "__main__":
    with open("test.json", encoding="utf-8") as f:
        dictionary = json.load(f)

    dictionary = [JSONDictionaryItem.from_dict(d) for d in dictionary]
    print(dictionary)
