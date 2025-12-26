#!/usr/bin/env python

import os
import subprocess
import sys
from parser import parser
from pathlib import Path

from tokenizer import Token, tokenizer
from util import CursorStream


class BuiltIns:
    def exit(self, args: list[str]) -> None:
        sys.exit(0)

    def echo(self, args: list[str]) -> None:
        print(" ".join(args))

    def pwd(self, args: list[str]) -> None:
        print(Path.cwd())

    def cd(self, args: list[str]) -> None:
        if not args:
            return

        target_dir = args[0]
        if not Path(target_dir).is_dir():
            print(f"cd: {target_dir}: No such file or directory")
            return

        os.chdir(target_dir)

    def type(self, args: list[str]) -> None:
        name = args[0]

        # check builtins
        builtin_func = getattr(self, name, None)
        if callable(builtin_func):
            print(f"{name} is a shell builtin")
            return

        # check PATH
        paths = os.environ.get("PATH", "").split(os.pathsep)
        for path in paths:
            file_path = Path(path) / name
            if file_path.is_file() and os.access(file_path, os.X_OK):
                print(f"{name} is {file_path}")
                return

        print(f"{name}: not found")


class Shell:
    def __init__(self):
        self.blah = None

    def read(self, text: str) -> None:
        tokens = CursorStream[Token](it=tokenizer(text))
        self.blah = parser(tokens)

    def eval(self) -> None:
        if self.blah.command.name is None:
            return

        builtin = getattr(BuiltIns(), self.blah.command.name, None)
        if callable(builtin):
            builtin(self.blah.command.args)
            return

        paths = os.environ.get("PATH", "").split(os.pathsep)
        for path in paths:
            file_path = Path(path) / self.blah.command.name
            if file_path.is_file() and os.access(file_path, os.X_OK):
                subprocess.run([self.blah.command.name] + self.blah.command.args)
                return

        print(f"{self.blah.command.name}: not found")


if __name__ == "__main__":
    shell = Shell()
    while True:
        shell.read(text=input("$ "))
        shell.eval()
