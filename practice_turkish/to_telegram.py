from practice_turkish.filepath import prompt_filepath, prompt_dictionary_type
from practice_turkish.dictionaries import Dictionary


def send_to_telegram() -> None:
    """Send a dictionary to a telegram user via the bot.

    Prompts a dictionary type and filename, loads the dictionary and sends it 
    telegram user via the bot.
    """
    dictionary_entry_type = prompt_dictionary_type()
    path = prompt_filepath(
        message="Choose file to send to you via telegram: ",
        is_file=True,
        extension=dictionary_entry_type.extension(),
        directory=dictionary_entry_type.default_directory(),
    )
    dictionary = Dictionary.from_file(path, dictionary_entry_type)
    dictionary.send_to_telegram()


def main() -> None:
    """If open as a script, run make translate function."""
    send_to_telegram()


if __name__ == "__main__":
    main()
