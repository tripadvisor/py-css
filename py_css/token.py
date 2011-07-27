class Token:
    pass

class Whitespace(Token):
    @staticmethod
    def matches():
        return (' ', '\n', '\r', '\f', '\0', '\b', '\t', '\v')

class Slash(Token):
    @staticmethod
    def matches():
        return ('/')

class Star(Token):
    @staticmethod
    def matches():
        return ('*')

class Quote(Token):
    @staticmethod
    def matches():
        return ('"', "'")

class Equals(Token):
    @staticmethod
    def matches():
        return ('=')

class Colon(Token):
    @staticmethod
    def matches():
        return (':')

class Period(Token):
    @staticmethod
    def matches():
        return ('.')

class Hyphen(Token):
    @staticmethod
    def matches():
        return ('-')

class LeftBrace(Token):
    @staticmethod
    def matches():
        return ('{')

class RightBrace(Token):
    @staticmethod
    def matches():
        return ('}')

class RightBracket(Token):
    @staticmethod
    def matches():
        return (']')

class LeftParen(Token):
    @staticmethod
    def matches():
        return ('(')

class GT(Token):
    @staticmethod
    def matches():
        return ('>')

class Comma(Token):
    @staticmethod
    def matches():
        return (',')

class SemiColon(Token):
    @staticmethod
    def matches():
        return (';')

TOKENS = [Whitespace, Slash, Star, Quote, Equals, Colon, Period,
          Hyphen, LeftBrace, RightBrace, RightBracket, LeftParen,
          GT, Comma, SemiColon]
TOKEN_MAP = {}

for token in TOKENS:
    for char in token.matches():
        TOKEN_MAP[char] = token

def tokenize(char):
    """Return the token for the given character."""
    if char in TOKEN_MAP:
        return TOKEN_MAP[char]
    return Token

