from tokenizer import Token, tokenizer
from util import CursorStream

####################################################
# NODES
####################################################


class CommandNode:
    def __init__(self, name: str, args: list[str]):
        self.name = name
        self.args = args

    def __repr__(self):
        return f"CommandNode({self.name}, args={self.args})"


class RedirectNode:
    def __init__(self, file_descriptor: int, target: str):
        self.fd = file_descriptor
        self.target = target

    def __repr__(self):
        return f"RedirectNode({self.fd}, {self.target})"


class CommandLineNode:
    def __init__(self, command: CommandNode, redirects: list[RedirectNode] | None):
        self.command = command
        self.redirects = redirects

    def __repr__(self):
        return f"CommandLineNode({self.command}, redirects=[{self.redirects}])"


####################################################
# PARSERS
####################################################


def found_redirect(tokens: CursorStream[Token]) -> bool:
    if tokens.current is None:
        return False
    if tokens.current.is_redirect_op():
        return True

    if tokens.current.is_number():
        if tokens.next is None:
            return False
        if tokens.next.is_redirect_op():
            return True
    return False


def parse_command(tokens: CursorStream[Token]) -> CommandNode:
    # if tokens.current is None or tokens.current.is_not_word_like():
    #     raise SyntaxError("Expected command name")

    command = tokens.current.value
    tokens.advance()

    args = []
    while (
        tokens.current is not None
        and tokens.current.is_word_like()
        and not found_redirect(tokens)
    ):
        args.append(tokens.current.value)
        tokens.advance()

    return CommandNode(name=command, args=args)


def parse_redirection(tokens: CursorStream[Token]) -> RedirectNode:
    if tokens.current is None:
        raise SyntaxError("Unexpected end of input while parsing redirection")

    file_descriptor: int | None = None

    # check current token is a number and next token is a redirect operation
    if tokens.current.is_number():
        if tokens.next is None:
            raise SyntaxError("Unexpected end of input while parsing redirection")
        if tokens.next.is_redirect_op():
            file_descriptor = int(tokens.current.value)
            tokens.advance()

    if tokens.current is None or not tokens.current.is_redirect_op():
        raise SyntaxError("Expected '>' in redirection")
    tokens.advance()

    if tokens.current is None or tokens.current.is_not_word_like():
        print(tokens.current)
        raise SyntaxError("Expected file name after '>'")
    file_name = tokens.current.value
    tokens.advance()

    if file_descriptor is None:
        file_descriptor = 1

    return RedirectNode(file_descriptor=file_descriptor, target=file_name)


def parser(tokens: CursorStream[Token]) -> CommandLineNode:
    command: CommandNode = parse_command(tokens)

    redirects: list[RedirectNode] = []
    while found_redirect(tokens):
        redirects.append(parse_redirection(tokens))

    # if tokens.current is None or not tokens.current.is_eof():
    #     raise SyntaxError(f"Unexpected token at end of input: {tokens.current}")

    return CommandLineNode(command=command, redirects=redirects)


if __name__ == "__main__":
    text = "echo hello, world!"
    tokens = CursorStream[Token](it=tokenizer(text))
    print(parser(tokens))
