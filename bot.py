from configparser import ConfigParser, SectionProxy
from dataclasses import dataclass

import requests


class TelegramError(Exception):
    pass


class ConfigurationError(TelegramError):
    pass


class AuthenticationError(TelegramError):
    pass


@dataclass
class APIConfiguration:
    url: str
    user_id: int
    token: str

    @classmethod
    def from_config(cls, path: str = "config.ini") -> "APIConfiguration":
        config = ConfigParser()
        if not config.read(path):
            raise ConfigurationError(
                f"Missing '{path}' configuration file!"
            )

        try:
            API_section = config["BOT API"]
        except KeyError:
            raise ConfigurationError(
                f"Configuration file '{path}' is incorrect: missing 'BOT API' section."
            )

        URL = _get_and_check_str(API_section, "URL", path)
        user_id = _get_and_check_int(API_section, "USER ID", path)
        token = _get_and_check_str(API_section, "TOKEN", path)

        return cls(URL, user_id, token)


def send_to_telegram(
    url: str,
    user_id: int,
    token: str,
    text: str,
) -> bool:
    response = requests.post(
        url=url,
        data={
            "user id": user_id,
            "token": token,
            "text": text
        }
    )
    if response.status_code == 403:
        raise AuthenticationError(
            "User token is rejected!\nPlease, check 'USER ID' and 'TOKEN' fields in your configuration file."
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
