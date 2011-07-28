class Token:
    @staticmethod
    def process(state, c):
        state.space = False
        state.hold(c)

class Whitespace(Token):
    @staticmethod
    def matches():
        return (' ', '\n', '\r', '\f', '\0', '\b', '\t', '\v')
    
    @staticmethod
    def process(state, c):
        tmp = state.get_tmp()
        if state.rgb:
            if tmp:
                state.append('%02x' % int(tmp[:-1]))
            state.clear()
        else:
            if not state.boundary:
                state.set_append(' ')
            if tmp:
                state.ready(None)
                if tmp[-1] != '/':
                    state.boundary = False
            else:
                state.clear()
            state.space = True

class Slash(Token):
    @staticmethod
    def matches():
        return ('/')

    @staticmethod
    def process(state, c):
        if not state.boundary and state.get_tmp():
            state.append(' ')
        state.boundary = True
        state.space = False
        state.hold(c)

class Star(Token):
    @staticmethod
    def matches():
        return ('*')

    @staticmethod
    def process(state, c):
        if state.get_tmp() == '/' and (not state.get_buffer() or state.get_buffer()[-1] != '>'):
            state.comment = True
        state.space = False
        state.hold(c)

class Quote(Token):
    @staticmethod
    def matches():
        return ('"', "'")

    @staticmethod
    def process(state, c):
        if not state.skip:
            if c == '"':
                state.quote = True
            if c == "'":
                state.squote = True
        if not state.boundary:
            state.append(' ')
        state.boundary = True
        state.space = False
        state.ready(c)

class Equals(Token):
    @staticmethod
    def matches():
        return ('=')

    @staticmethod
    def process(state, c):
        if not state.boundary:
            state.append(' ')
        state.boundary = True
        state.space = False
        state.ready(c);

class Colon(Token):
    @staticmethod
    def matches():
        return (':')

    @staticmethod
    def process(state, c):
        if state.space and not state.rule:
            state.append(' ')
        state.boundary = True
        state.space = False
        state.ready(c)

class Period(Token):
    @staticmethod
    def matches():
        return ('.', '-')

    @staticmethod
    def process(state, c):
        if not state.rule:
            if state.space and not state.boundary:
                state.append(' ')
            state.boundary = True
            state.ready(c)
        else:
            state.hold(c)
        state.space = False        

class LeftBrace(Token):
    @staticmethod
    def matches():
        return ('{')

    @staticmethod
    def process(state, c):
        if not state.boundary and state.get_tmp():
            state.append(' ')
        state.boundary = True
        state.space = False
        state.rule = True
        state.ready(c)

class RightBrace(Token):
    @staticmethod
    def matches():
        return ('}')

    @staticmethod
    def process(state, c):
        if not state.boundary and state.get_tmp():
            state.append(' ')
        state.boundary = True
        state.space = False
        state.rule = False
        state.ready(c)

class RightBracket(Token):
    @staticmethod
    def matches():
        return (']')

    @staticmethod
    def process(state, c):
        state.boundary = False
        state.space = False
        state.ready(c)

class LeftParen(Token):
    @staticmethod
    def matches():
        return ('(')

    @staticmethod
    def process(state, c):
        if not state.boundary:
            state.append(' ')
        state.boundary = True
        state.space = True
        state.ready(c)

class GT(Token):
    @staticmethod
    def matches():
        return ('>')

    @staticmethod
    def process(state, c):
        state.boundary = True
        state.space = False
        state.ready(c)

class Comma(Token):
    @staticmethod
    def matches():
        return (',')

    @staticmethod
    def process(state, c):
        state.boundary = True
        state.space = False
        if state.rgb:
            state.append('%02x' % int(state.get_tmp()))
            state.clear()
        else:
            state.ready(c)

class SemiColon(Token):
    @staticmethod
    def matches():
        return (';')

    @staticmethod
    def process(state, c):
        if not state.boundary:
            state.append(' ')
        state.boundary = True
        state.space = False
        if state.skip:
            state.skip = False
        else:
            buf = state.get_buffer()
            if state.rgb:
                state.append('%02x' % int(state.get_tmp()[:-1]))
                app = state.get_append()
                if (len(app) >= 2 and app[0] == app[1] and
                        buf[-1] == buf[-2] and buf[-3] == buf[-4]):
                    state.set_append(buf[-3]).append(buf[-1]).append(app[0])
                    state.set_buffer(buf[:-4])
                state.append(c).clear()
                state.rgb = False
            else:
                state.ready(c if (buf[-1] != ';' and buf[-1] != '{') else '')
                state.rgb = False

TOKENS = [Whitespace, Slash, Star, Quote, Equals, Colon, Period,
          LeftBrace, RightBrace, RightBracket, LeftParen,
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

