import random
from enum import Enum
from functools import partial
from typing import Optional, Callable

from rich import print
import typer
from InquirerPy import inquirer
from InquirerPy.base.control import Choice

from practice_turkish.languages import Language, PrompterInTheLanguage


class Difficulty(str, Enum):
    """An enum used to represent difficulty."""

    DIGITS = "DIGITS"
    TENS = "TENS"
    BASIC = "BASIC"
    ADVANCED = "ADVANCED"


TEN = 10
ONE_HUNDRED = 100
ONE_THOUSAND = 1_000
ONE_MILLION = 1_000_000
ONE_BILLION = 1_000_000_000

digits = {
    0: "sıfır",
    1: "bir",
    2: "iki",
    3: "üç",
    4: "dört",
    5: "beş",
    6: "altı",
    7: "yedi",
    8: "sekiz",
    9: "dokuz",
}

tens = {
    0: "",
    10: "on",
    20: "yirmi",
    30: "otuz",
    40: "kırk",
    50: "elli",
    60: "altmış",
    70: "yetmiş",
    80: "seksen",
    90: "doksan",
}

more = {
    ONE_HUNDRED: "yüz",
    ONE_THOUSAND: "bin",
    ONE_MILLION: "milyon",
    ONE_BILLION: "milyar",
}


def spell_small_number(number: int, dismiss_one: bool = False) -> str:
    """Spell a positive integer number lesser than 1000 in turkish.

    Parameters
    ----------
    number : int
        A positive integer number to spell. 0 <= number <= 999.
    dismiss_one : bool
        Whether to put 'bir' in front or note. Necessary, since
        `bin` used instead of `bir bin`.

    Returns
    ----------
    spelling : str
        A line of text with spelling of the number in turkish.
    """
    if number not in range(1000):
        raise ValueError("The number isn't a positive integer number lesser than 999.")

    if dismiss_one and number == 1:
        return ""

    n_hundreds, reminder = divmod(number, ONE_HUNDRED)
    n_tens, n_ones = divmod(reminder, TEN)

    match n_hundreds:
        case 0:
            hundred = ""
        case 1:
            hundred = "yüz"
        case _:
            hundred = digits[n_hundreds] + " yüz"
    ten = tens[n_tens * 10]
    one = digits[n_ones] if n_ones > 0 else ""
    return f"{hundred} {ten} {one}".strip()


def spell_number(number: int) -> str:
    """Spell a positive integer number lesser than 10^12 in turkish.

    Parameters
    ----------
    number : int
        A positive integer number to spell. 0 <= number <= 10^12.

    Returns
    ----------
    spelling : str
        A line of text with spelling of the number in turkish.
    """
    if number not in range(10**12):
        raise ValueError("Too big number")

    if number == 0:
        return digits[0]

    n_billions, reminder = divmod(number, ONE_BILLION)
    n_millions, reminder = divmod(reminder, ONE_MILLION)
    n_thousands, reminder = divmod(reminder, ONE_THOUSAND)

    parts = []
    if n_billions:
        parts.append(f"{spell_small_number(n_billions)} milyar".strip())

    if n_millions:
        parts.append(f"{spell_small_number(n_millions)} milyon".strip())

    if n_thousands:
        parts.append(f"{spell_small_number(n_thousands, True)} bin".strip())

    parts.append(spell_small_number(reminder))
    return " ".join(parts).strip()


def prompt_difficulty() -> Difficulty:
    """Prompt the difficulty from the user.

    Returns
    ----------
    difficulty : Difficulty
        A value from `Difficulty` enum.
    """
    return inquirer.select(
        message="Choose difficulty:",
        choices=[
            Choice(value=Difficulty.DIGITS, name="digits"),
            Choice(value=Difficulty.TENS, name="tens"),
            Choice(value=Difficulty.BASIC, name="basic"),
            Choice(value=Difficulty.ADVANCED, name="advanced"),
        ],
    ).execute()


def numbers(
    difficulty: Optional[Difficulty] = typer.Option(
        None, "--difficulty", help="Difficulty"
    )
) -> None:
    """Practice session for numbers.

    Parameters
    ----------
    difficulty : Optional[Difficulty]
        A value from `Difficulty` enum. Prompted from user if None.
    """
    if difficulty is None:
        difficulty = prompt_difficulty()

    number_generator: Callable
    match difficulty:
        case difficulty.DIGITS:
            number_generator = partial(random.choice, list(digits.keys()))
        case difficulty.TENS:
            number_generator = partial(random.choice, list(tens.keys()))
        case difficulty.BASIC:
            number_generator = partial(
                random.choice, list((digits | tens | more).keys())
            )
        case difficulty.ADVANCED:
            number_generator = partial(random.randrange, 10**12)

    prompter = PrompterInTheLanguage(Language.turkish)
    while True:
        number = number_generator()
        correct_answer = spell_number(number)
        print(
            f"Spell [yellow]{number:10_}[/yellow]. Press [blue]enter[/blue] to escape."
        )
        user_answer = prompter.prompt()
        if not user_answer:
            return
        if user_answer.split() == correct_answer.split():
            print("[green]Correct![/green]")
        else:
            print(
                f"[red]Incorrect![/red] Right answer:\n> [green]{correct_answer}[/green]"
            )


def main() -> None:
    """If open as a script, run make number function."""
    typer.run(numbers)


if __name__ == "__main__":
    main()
