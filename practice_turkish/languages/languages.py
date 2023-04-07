from enum import Enum
from typing import Any

from InquirerPy import inquirer
from InquirerPy.base.control import Choice

from practice_turkish.languages.turkishinput import prompt_turkish
from practice_turkish.languages.russianinput import prompt_russian
from practice_turkish.languages.englishinput import prompt_english


class Language(str, Enum):
    "An enumeration used to represent natural languages."
    turkish = "turkish"
    russian = "russian"
    english = "english"


class PrompterInTheLanguage:
    """A class used to prompt from the user in specified language.

    Attributes
    ----------
    prompt_function : Callable[[str, str], str]
        One of the prompt_turkish, prompt_russian or prompt_english functions.

    Methods
    ----------
    prompt(self, message: str = "> ", additional_symbols: str = "") -> str:
        Prompt the user in the specified language
    """

    def __init__(self, language: Language) -> None:
        match language:
            case Language.turkish:
                self.prompt_function = prompt_turkish
            case Language.russian:
                self.prompt_function = prompt_russian
            case Language.english:
                self.prompt_function = prompt_english

    def prompt(
        self, message: str = "> ", additional_symbols: str = "", **kwargs: Any
    ) -> str:
        "Prompt the user in the specified language"
        return self.prompt_function(message, additional_symbols, **kwargs)


language_map = {
    Language.turkish: "Türkçe",
    Language.russian: "Русский",
    Language.english: "English",
}


def prompt_language(message: str) -> Language:
    """Prompt a language from the user by picking from values of `Language` enum.

    Parameters
    ----------
    message : str
        A text to be printed before the prompt.

    Returns
    ----------
    language : Language
        A value of `Language` enum.
    """
    return inquirer.select(
        message=message,
        choices=[Choice(value=key, name=value) for key, value in language_map.items()],
    ).execute()


def prompt_way_of_translation(language_a: Language, language_b: Language) -> bool:
    """Prompt a way of translation: language A ➔ language B or vice versa.

    Parameters
    ----------
    language_a : Language
        Language A.
    language_b : Language
        Language B

    Returns
    ----------
    a2b : bool
        True, if the user picked to translate from language A to language B.
        False, if the user picked to translate from language B to language A.
    """
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
