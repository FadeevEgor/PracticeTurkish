import random
from enum import Enum
from functools import partial

from rich import print
import typer
from InquirerPy import inquirer
from InquirerPy.base.control import Choice

from turkishinput import prompt_turkish


class Difficulty(str, Enum):
    digits = "digits"
    tens = "tens"
    basic = "basic"
    advanced = "advanced"


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
    0:  "",
    10: "on",
    20: "yirmi",
    30: "otuz",
    40: "kırk",
    50: "elli",
    60: "altmış",
    70: "yetmiş",
    80: "seksen",
    90: "doksan"
}

more = {
    ONE_HUNDRED: "yüz",
    ONE_THOUSAND: "bin",
    ONE_MILLION: "milyon",
    ONE_BILLION: "milyar"
}


def spell_small_number(number: int, dismiss_one: bool = False) -> str:
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
    ten = tens[n_tens*10]
    one = digits[n_ones] if n_ones > 0 else ""
    return f"{hundred} {ten} {one}".strip()


def spell(number: int) -> str:
    if number > 999_999_999_999:
        raise ValueError("Too big number")

    if number == 0:
        return digits[0]

    n_billions, reminder = divmod(number, ONE_BILLION)
    n_millions, reminder = divmod(reminder, ONE_MILLION)
    n_thousands, reminder = divmod(reminder, ONE_THOUSAND)

    parts = []
    if n_billions:
        parts.append(
            f"{spell_small_number(n_billions)} milyar".strip()
        )

    if n_millions:
        parts.append(
            f"{spell_small_number(n_millions)} milyon".strip()
        )

    if n_thousands:
        parts.append(
            f"{spell_small_number(n_thousands, True)} bin".strip()
        )

    parts.append(spell_small_number(reminder))
    return " ".join(parts).strip()


def prompt_difficulty() -> Difficulty:
    return inquirer.select(
        message="Choose difficulty:",
        choices=[
            Choice(value=Difficulty.digits, name="digits"),
            Choice(value=Difficulty.tens, name="tens"),
            Choice(value=Difficulty.basic, name="basic"),
            Choice(value=Difficulty.advanced, name="advanced"),
        ],
    ).execute()


def numbers(
        difficulty: Difficulty = typer.Option(
            None, "--difficulty", help="Difficulty"
        )
):
    if difficulty is None:
        difficulty = prompt_difficulty()

    match difficulty:
        case difficulty.digits:
            number_generator = partial(random.choice, list(digits.keys()))
        case difficulty.tens:
            number_generator = partial(random.choice, list(tens.keys()))
        case difficulty.basic:
            number_generator = partial(
                random.choice, list((digits | tens | more).keys())
            )
        case difficulty.advanced:
            number_generator = partial(random.randrange, 1_000_000_000_000)

    while True:
        number = number_generator()
        correct_answer = spell(number)
        print(
            f"Spell [yellow]{number:10_}[/yellow]. Press [blue]enter[/blue] to escape."
        )
        user_answer = prompt_turkish()
        if not user_answer:
            return
        if user_answer.split() == correct_answer.split():
            print("[green]Correct![/green]")
        else:
            print(
                f"[red]Incorrect![/red] Right answer:\n> [green]{correct_answer}[/green]")


if __name__ == "__main__":
    typer.run(numbers)
