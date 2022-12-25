

from abc import ABC, abstractmethod
from russianinput import prompt_russian
from turkishinput import prompt_turkish


class DictionaryItem(ABC):
    def ask_translation_to_russian(self) -> bool:
        question = f"{self.turkish} -> "
        answer = prompt_russian(question)
        return self.check_translation_to_russian(answer)

    def ask_translation_to_turkish(self) -> bool:
        question = f"{self.russian} -> "
        answer = prompt_turkish(question)
        return self.check_translation_to_turkish(answer)

    @abstractmethod
    def check_translation_to_russian(self, answer: str) -> bool:
        pass

    @abstractmethod
    def check_translation_to_turkish(self, answer: str) -> bool:
        pass
