from collections.abc import Iterator
from enum import Enum, auto

from util import CursorStream


class TokenKind(Enum):
    COMMAND_UNIT = auto()
    SINGLE_QUOTE = auto()
    DOUBLE_QUOTE = auto()
    BACKSLASH = auto()
    REDIRECT = auto()
    EOF = auto()


class Token:
    def __init__(self, kind: TokenKind, value: str | None = None):
        self.kind: TokenKind = kind
        self.value: str | None = value

    def __repr__(self) -> str:
        if self.value:
            return f"Token({self.kind}: {self.value})"
        else:
            return f"Token({self.kind})"

    def is_word_like(self) -> bool:
        return self.kind in (
            TokenKind.COMMAND_UNIT,
            TokenKind.SINGLE_QUOTE,
            TokenKind.DOUBLE_QUOTE,
        )

    def is_not_word_like(self) -> bool:
        return self.kind not in (
            TokenKind.COMMAND_UNIT,
            TokenKind.SINGLE_QUOTE,
            TokenKind.DOUBLE_QUOTE,
        )

    def is_redirect_op(self) -> bool:
        return self.kind == TokenKind.REDIRECT

    def is_number(self) -> bool:
        return self.kind == TokenKind.COMMAND_UNIT and self.value.isdigit()

    def is_eof(self) -> bool:
        return self.kind == TokenKind.EOF


class TokenQueue:
    def __init__(self):
        self.head: Token | None = None
        self.tail: Token | None = None
        self.length: int = 0

    def __iter__(self):
        current = self.head
        while current:
            yield current
            current = current.next

    def __len__(self):
        return self.length

    def __getitem__(self, index: int) -> Token:
        if index < 0:
            raise IndexError
        if index >= self.length:
            raise IndexError
        current = self.head
        for _ in range(index):
            current = current.next
        return current

    def __repr__(self):
        tokens = []
        current = self.head
        while current:
            tokens.append(repr(current))
            current = current.next
        return " -> ".join(tokens)

    def push(self, token: Token):
        self.length += 1
        if self.head is None:  # Queue is empty
            self.head = token
            self.tail = token
            return
        self.tail.next = token
        self.tail = token

    def pop(self):
        if self.head is None:  # Queue is empty
            return None
        self.length -= 1
        if self.head.next:
            token = self.head
            self.head = self.head.next
            return token
        token = self.head
        self.head = None
        self.tail = None
        return token


def tokenizer(text: str) -> Iterator[Token]:
    char = CursorStream[str](it=iter(text))

    while char.current is not None:

        # DELIMITERS
        # ----------
        if char.current in " \t":
            char.advance()
            continue

        # SINGLE_QUOTE
        # ------------
        if char.current == "'":
            single_quote_str = ""
            char.advance()  # advance past first quote

            while True:
                if char.current is None:
                    raise SyntaxError("Unterminated single-quoted string")
                if char.current == "'":
                    break

                single_quote_str += char.current
                char.advance()

            char.advance()  # advance past last quote

            yield Token(kind=TokenKind.SINGLE_QUOTE, value=single_quote_str)
            continue

        # DOUBLE_QUOTE
        # ------------
        if char.current == '"':
            double_quote_str = ""
            char.advance()  # advance the first quote

            while True:
                if char.current is None:
                    raise SyntaxError("Unterminated double-quoted string")
                if char.current == '"':
                    break

                double_quote_str += char.current
                char.advance()

            char.advance()  # advance the last quote

            yield Token(kind=TokenKind.DOUBLE_QUOTE, value=double_quote_str)
            continue

        # REDIRECT
        # --------
        if char.current == ">":
            yield Token(kind=TokenKind.REDIRECT)
            char.advance()
            continue

        # COMMAND_UNIT
        # ------------
        if char.current not in " \t\n'\"|&;<>()":
            command_unit = ""

            while True:
                if char.current is None:  # EOF
                    break
                if char.current in " \t\n":  # delimiters
                    break
                if char.current in "'\"|&;<>()":  # Invalid characters
                    break

                command_unit += char.current
                char.advance()

            yield Token(kind=TokenKind.COMMAND_UNIT, value=command_unit)
            continue

        raise Exception(f'Undefinded character -> "{char.current}"')

    # EOF
    # ---
    yield Token(TokenKind.EOF)


if __name__ == "__main__":
    text = "hello, world! 1>hello.txt"

    tokens = CursorStream[Token](it=tokenizer(text))

    print(tokens.current)
    tokens.advance()
    print(tokens.current)
    tokens.advance()
    print(tokens.current)
    tokens.advance()
    print(tokens.current)
    tokens.advance()
    print(tokens.current)
    tokens.advance()
    print(tokens.current)
    tokens.advance()
    print(tokens.current)
