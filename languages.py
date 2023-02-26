from enum import Enum

from InquirerPy import inquirer
from InquirerPy.base.control import Choice

from turkishinput import prompt_turkish
from russianinput import prompt_russian
from englishinput import prompt_english


class Language(str, Enum):
    turkish = "turkish"
    russian = "russian"
    english = "english"


class PrompterInTheLanguage:
    def __init__(self, language: Language) -> None:
        match language:
            case Language.turkish:
                self.prompt_function = prompt_turkish
            case Language.russian:
                self.prompt_function = prompt_russian
            case Language.english:
                self.prompt_function = prompt_english

    def __call__(
        self,
        message: str = "> ",
        additional_symbols: str = "",
        **kwargs
    ) -> str:
        return self.prompt_function(message, additional_symbols, **kwargs)


language_map = {
    Language.turkish: "Türkçe",
    Language.russian: "Русский",
    Language.english: "English"
}


def prompt_way_of_translation(language_a: Language, language_b: Language) -> bool:
    la, lb = language_map[language_a], language_map[language_b]
    max_len = max(len(la), len(lb))
    la, lb = la.ljust(max_len), lb.ljust(max_len)
    return inquirer.select(
        message="Choose language you want to translate to.",
        choices=[
            Choice(value=True, name=f"{la} → {lb}"),
            Choice(value=False, name=f"{lb} → {la}"),
        ],
    ).execute()


def prompt_language(message: str) -> Language:
    return inquirer.select(
        message=message,
        choices=[
            Choice(value=key, name=value)
            for key, value in language_map.items()
        ]
    ).execute()
