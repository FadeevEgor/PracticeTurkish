

from abc import ABC, abstractmethod
from russianinput import prompt_russian
from turkishinput import prompt_turkish


class DictionaryItem(ABC):
    """
    An ABC for a dictionary item.
    Is used in order to practice translation.
    """

    def ask_translation_to_russian(self) -> str:
        question = f"{self.turkish} -> "
        return prompt_russian(question)

    def ask_translation_to_turkish(self) -> str:
        question = f"{self.russian} -> "
        return prompt_turkish(question)

    @abstractmethod
    def check_translation_to_russian(self, answer: str) -> bool:
        pass

    @abstractmethod
    def check_translation_to_turkish(self, answer: str) -> bool:
        pass
