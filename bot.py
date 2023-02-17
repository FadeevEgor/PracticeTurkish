from configparser import ConfigParser
from dataclasses import dataclass

import requests


class ConfigurationError(Exception):
    pass


class WrongToken(Exception):
    pass


@dataclass
class APIConfiguration:
    url: str
    user_id: int
    token: str

    @classmethod
    def from_config(cls, path: str = "config.ini") -> "APIConfiguration":
        config = ConfigParser()
        config.read(path)
        API_section = config["BOT API"]
        return cls(
            API_section["URL"],
            API_section["USER ID"],
            API_section["TOKEN"]
        )


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
        raise WrongToken("User token is wrong. Check your configuration file!")
    if response.status_code != 200:
        raise requests.HTTPError(response.text)
    return True
