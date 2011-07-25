#!/usr/bin/env python

class Token:
    def matches(self, char):
        return True

class Whitespace(Token):
    def matches(self, char):
        return char in (' ', '\n', '\r', '\f', '\0', '\b', '\t', '\v')

class Slash(Token):
    def matches(self, char):
        return char == '/'

class Star(Token):
    def matches(self, char):
        return char == '*'

class Quote(Token):
    def matches(self, char):
        return char in ('"', "'")

class Equals(Token):
    def matches(self, char):
        return char == '='

class Colon(Token):
    def matches(self, char):
        return char == ':'

class Period(Token):
    def matches(self, char):
        return char == '.'

class Hyphen(Token):
    def matches(self, char):
        return char == '-'

class LeftBrace(Token):
    def matches(self, char):
        return char == '{'

class RightBrace(Token):
    def matches(self, char):
        return char == '}'

class RightBracket(Token):
    def matches(self, char):
        return char == ']'

class LeftParen(Token):
    def matches(self, char):
        return char == '('

class GT(Token):
    def matches(self, char):
        return char == '>'

class Comma(Token):
    def matches(self, char):
        return char == ','

class SemiColon(Token):
    def matches(self, char):
        return char == ';'

TOKENS = [Whitespace(), Slash(), Star(), Quote(), Equals(), Colon(), Period(),
          Hyphen(), LeftBrace(), RightBrace(), RightBracket(), LeftParen(),
          GT(), Comma(), SemiColon(), Token()]

def tokenize(char):
    """Return the token for the given character.
    """
    for token in TOKENS:
        if token.matches(char):
            return token
    return Token()

def ncss(str):
    """Minify a string of CSS.
    """
    buf = ''
    tmp = ''
    app = ''
    boundary = True
    charset  = False
    comment  = False
    skip     = False
    rgb      = False
    quote    = False
    squote   = False
    ie5mac   = False
    filter   = False
    space    = False
    media    = False
    rule     = False

    for i, c in enumerate(str):
        if comment:
            tmp += c
            if c == '/' and str[i-1] == '*':
                if str[i-2] == '\\': # ie5mac hack
                    buf == '/*\\*/'
                    ie5mac = True
                elif ie5mac:
                    buf += '/**/'
                    ie5mac = False
                elif tmp[2] == '!':
                    buf += c
                tmp = ''
                comment = False
            continue

        if quote or squote:
            buf += c
            if ((quote and c == '"') or (squote and c == "'")) and str[i-1] != '\\':
                quote = False
                squote = False
                if filter and str[i-1] == ')':
                    #buf = buf.replace(IEALPHA, '')
                    filter = false
            continue

        app = ''
        token = tokenize(c).__class__

        if token == Whitespace:
            if rgb:
                if len(tmp) > 0:
                    app += hex(tmp[0:-1])
                tmp = ''
            else:
                if not boundary:
                    app = ' '
                if len(tmp) > 0:
                    app += tmp
                    if app[-1] != '/':
                        boundary = False
                tmp = ''
                space = True
        elif token == Slash:
            space = False
        else:
            tmp += c
            space = False

        if len(app) > 0:
            # charset
            # rgb
            if not skip:
                # lowercase
                # }
                # filter

                # zero values
                # small floats

                buf += app

    return buf


if __name__ == "__main__":
    import sys
    css = sys.stdin.read()
    m = ncss(css)
    sys.stdout.write(m)

