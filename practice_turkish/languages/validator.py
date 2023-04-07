from abc import ABC
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.document import Document


class SymbolValidator(Validator, ABC):
    """A class used to validate an input in a language.

    Used by the `prompt` function from `prompt_toolkit` library to ensure that
    user types in only symbols from alphabet of the language. Extends `Validator`
    class given by the library and overloads the `validate` method. Each subclass
    should overload `valid_symbols` class attribute.
    """

    valid_symbols: set[str] = set()

    def __init__(self, additional_symbols: str = "") -> None:
        super().__init__()
        self.valid_symbols |= set(list(additional_symbols))

    def validate(self, document: Document) -> None:
        """Check if all typed in symbols are permissible.

        Parameters
        ----------
        document : Document
            A current state of prompting session.

        Raises
        ----------
        ValidationError
            If the document contains prohibited symbols.
        """
        for i, s in enumerate(document.text):
            if s not in self.valid_symbols:
                raise ValidationError(
                    message="This input contains symbols out of Russian alphabet.",
                    cursor_position=i,
                )
