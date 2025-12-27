#!/usr/bin/env python

# import sys
import os
import subprocess
from parser import parser
from pathlib import Path

from tokenizer import Token, tokenizer
from util import CursorStream


class BuiltIns:
    def exit(self, args: list[str]) -> str | None:
        raise SystemExit(0)
        # sys.exit(0)

    def echo(self, args: list[str]) -> str:
        return " ".join(args)

    def pwd(self, args: list[str]) -> str:
        return str(Path.cwd())

    def cd(self, args: list[str]) -> str | None:
        if not args:
            return None

        target_dir = args[0]
        if not Path(target_dir).is_dir():
            return f"cd: {target_dir}: No such file or directory"

        os.chdir(target_dir)
        return None

    def type(self, args: list[str]) -> str:
        if not args:
            return ""

        name = args[0]

        # check builtins
        builtin_func = getattr(self, name, None)
        if callable(builtin_func):
            return f"{name} is a shell builtin"

        # check PATH
        paths = os.environ.get("PATH", "").split(os.pathsep)
        for path in paths:
            file_path = Path(path) / name
            if file_path.is_file() and os.access(file_path, os.X_OK):
                return f"{name} is {file_path}"

        return f"{name}: not found"


class Shell:
    def __init__(self):
        self.blah = None
        self.stdout = None
        self.stdout_path = None

    def read(self, text: str) -> None:
        tokens = CursorStream[Token](it=tokenizer(text))
        self.blah = parser(tokens)

    def eval(self) -> None:
        if self.blah.command.name is None:
            return

        for redirect in self.blah.redirects:
            if redirect.file_descriptor == 1:
                self.stdout_path = redirect.target_file

        builtin = getattr(BuiltIns(), self.blah.command.name, None)
        if callable(builtin):
            self.stdout = builtin(self.blah.command.args)
            return

        paths = os.environ.get("PATH", "").split(os.pathsep)
        for path in paths:
            file_path = Path(path) / self.blah.command.name
            if file_path.is_file() and os.access(file_path, os.X_OK):
                self.stdout = subprocess.run(
                    [str(file_path)] + self.blah.command.args,
                    capture_output=True,
                    text=True,
                ).stdout
                return

        self.stdout = f"{self.blah.command.name}: not found"
        return

    def print(self) -> None:
        stdout = self.stdout
        stdout_path = self.stdout_path

        self.stdout = None
        self.stdout_path = None

        if stdout is None:
            return

        if stdout_path is None:
            print(stdout)
            return

        with open(stdout_path, "w") as f:
            f.write(stdout)


if __name__ == "__main__":
    shell = Shell()
    while True:  # loop
        shell.read(text=input("$ "))
        shell.eval()
        shell.print()
