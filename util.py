from collections.abc import Iterator
from typing import Generic, Optional, TypeVar

T = TypeVar("T")


class CursorStream(Generic[T]):
    def __init__(self, it: Iterator[T]):
        self.it = it
        self.current: Optional[T] = None
        self.next: Optional[T] = next(self.it, None)
        self.advance()

    def advance(self) -> None:
        self.current = self.next
        self.next = next(self.it, None)

    def __iter__(self):
        return self

    def __next__(self) -> T:
        if self.current is None:
            raise StopIteration

        value = self.current
        self.advance()
        return value
