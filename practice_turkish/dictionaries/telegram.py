from configparser import ConfigParser, SectionProxy
from dataclasses import dataclass
import json
from typing import ClassVar

import requests


class TelegramError(Exception):
    "Generic error with regard to the bot API."


class ConfigurationError(TelegramError):
    "Raised when an error detected before trying to use it."


class AuthenticationError(TelegramError):
    "Raised when a pair of (user_id, token) is rejected by the bot."


@dataclass
class APIConfiguration:
    """
    A class used to represent a content of a configuration file.

    Attributes
    ----------
    url : str
        The url of the bot API.
        Should be correct in the `config.ini` file at the github repository.
    user_id : int
        The telegram ID number of the user messages are to be sent to.
        Should be an integer.
    token : str
        The token of the user messages are to be sent to.
        Should be a string of 8 symbols: latin letters (any case) and digits.
    """

    url: ClassVar[str] = "https://redirectfunction-d2ooxt72na-lm.a.run.app"
    user_id: int
    token: str

    @classmethod
    def read_ini(cls, path: str = "config.ini") -> "APIConfiguration":
        """Read configuration file from a file.

        Parameters
        ----------
        path : str
            A string representing a path to the configuration file.

        Raises
        ----------
        ConfigurationError
            If an error ocurred while reading the configuration from a file.
        """
        config = ConfigParser()
        if not config.read(path):
            raise ConfigurationError(f"Missing '{path}' configuration file!")

        try:
            API_section = config["BOT API"]
        except KeyError:
            raise ConfigurationError(
                f"Configuration file '{path}' is incorrect: missing 'BOT API' section."
            )

        user_id = _get_and_check_int(API_section, "USER ID", path)
        token = _get_and_check_str(API_section, "TOKEN", path)

        return cls(user_id, token)


def send_to_telegram(
    url: str,
    user_id: int,
    token: str,
    text: str,
) -> bool:
    """
    Sends message to a telegram user via the bot.

    Parameters
    ----------
    url : str
        The url of the bot.
    user_id : int
        The telegram ID number of the user messages are to be sent to.
        Should be an integer.
    token : str
        The token of the user messages are to be sent to.
        Should be a string of 8 symbols: latin letters (any case) and digits.
    text : str
        Text to send.

    Returns
    ----------
    x : bool
        True if no errors are detected, False otherwise.

    Raises
    ----------
    AuthenticationError
        If the pair (`user_id`, `token`) is rejected by the bot.
    """
    response = requests.post(
        url=url,
        data=json.dumps({"user id": user_id, "token": token, "text": text}),
        timeout=30,
    )
    if response.status_code == 403:
        raise AuthenticationError(
            """User token is rejected!
            Please, check 'USER ID' and 'TOKEN' fields in your configuration file."""
        )
    if response.status_code != 200:
        raise requests.HTTPError(response.text)
    return True


def _get_and_check_int(section: SectionProxy, field: str, path: str) -> int:
    try:
        value = section.getint(field)
    except ValueError:
        raise ConfigurationError(
            f"Configuration file '{path}' is incorrect: '{field}' expected to be an integer."
        )
    if value is None:
        raise ConfigurationError(
            f"Configuration file '{path}' is incorrect: missing '{field}' field."
        )
    return value


def _get_and_check_str(section: SectionProxy, field: str, path: str) -> str:
    try:
        value = section[field]
    except KeyError:
        raise ConfigurationError(
            f"Configuration file {path} is incorrect: missing '{field}' field."
        )
    return value
