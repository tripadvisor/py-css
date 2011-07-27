#!/usr/bin/env python

import re

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

ZERO_VALUES = re.compile(r'\b0(?:px|pt|in|cm|mm|em|%|pc|ex)')
SMALL_FLOATS = re.compile('0\.(\d+)(px|pt|in|cm|mm|em|%|pc|ex|)')
IEALPHA = re.compile('("?)(progid\:DXImageTransform\.Microsoft\.Alpha\(Opacity\=)(\d+)\)("?)', re.I)

def toHex(n):
    h = hex(int(n))[2:]
    if len(h) == 1: h = '0' + h
    return h

def minify(s, bufferOutput=True):
    """Minify a string of CSS.
    """
    buf = ''
    out = ''
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
    ruleEnd  = False

    for i, c in enumerate(s):
        if comment:
            tmp += c
            if c == '/' and s[i-1] == '*':
                if s[i-2] == '\\': # ie5mac hack
                    buf += '/*\\*/'
                    ie5mac = True
                elif ie5mac:
                    buf += '/**/'
                    ie5mac = False
                elif tmp[2] == '!': # important comments
                    buf += tmp
                tmp = ''
                comment = False
            continue

        if quote or squote:
            buf += c
            if ((quote and c == '"') or (squote and c == "'")) and s[i-1] != '\\':
                quote = False
                squote = False
                if filter and s[i-1] == ')':
                    buf = re.sub(IEALPHA, r'\1alpha(opacity=\3)\4', buf)
                    filter = false
            continue

        app = ''
        token = tokenize(c).__class__

        if token == Whitespace:
            if rgb:
                if len(tmp) > 0:
                    app += toHex(tmp[0:-1])
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
            if not boundary and len(tmp) > 0:
                app += ' '
            boundary = True
            space = False
            tmp += c
        elif token == Star:
            if tmp == '/' and (len(buf) == 0 or buf[-1] != '>'):
                comment = True
            space = False
            tmp += c
        elif token == Quote:
            if not skip:
                if c == '"': quote = True
                if c == "'": squote = True
            if not boundary: app += ' '
            boundary = True
            space = False
            app += tmp
            app += c
            tmp = ''
        elif token == Equals:
            if not boundary: app += ' '
            boundary = True
            space = False
            app += tmp
            app += c
            tmp = ''
        elif token == Colon:
            if space and not rule: app += ' '
            boundary = True
            space = False
            app += tmp
            app += c
            tmp = ''
        elif token == Period or token == Hyphen:
            if not rule:
                if space and not boundary: app += ' '
                boundary = True
                app += tmp
                app += c
                tmp = ''
            else:
                tmp += c
            space = False
        elif token == LeftBrace:
            if not boundary and len(tmp) > 0: app += ' '
            boundary = True
            space = False
            rule = True
            app += tmp
            app += c
            tmp = ''
        elif token == RightBrace:
            if not boundary and len(tmp) > 0: app += ' '
            boundary = True
            space = False
            rule = False
            app += tmp
            app += c
            tmp = ''
        elif token == RightBracket:
            boundary = False
            space = False
            app += tmp
            app += c
            tmp = ''
        elif token == LeftParen:
            if not boundary: app += ' '
            boundary = True
            space = True
            app += tmp
            app += c
            tmp = ''
        elif token == GT:
            boundary = True
            space = False
            app += tmp
            app += c
            tmp = ''
        elif token == Comma:
            boundary = True
            space = False
            if rgb:
                app += toHex(tmp)
            else:
                app += tmp
                app += c
            tmp = ''
        elif token == SemiColon:
            if not boundary: app += ' '
            boundary = True
            Space = False
            if skip:
                skip = False
            else:
                if rgb:
                    app += toHex(tmp[0:-1])
                    if len(app) >= 2 and app[0] == app[1] and\
                            buf[-1] == buf[-2] and buf[-3] == buf[-4]:
                        app = buf[-3] + buf[-1] + app[0]
                        buf = buf[0:-4]
                    app += c
                    tmp = ''
                    rgb = False
                else:
                    app += tmp
                    if buf[-1] != ';' and buf[-1] != '{':
                        app += ';'
                    tmp = ''
                    rgb = False
        else:
            tmp += c
            space = False

        if len(app) > 0:
            if app == '@charset':
                if charset:
                    skip = True
                else:
                    charset = True
                    buf += app
            elif app == ' rgb(':
                rgb = True
                buf += ' #'
            elif app == 'rgb(':
                rgb = True
                buf += '#'
            elif not skip:
                if rule and app[-1] != '{':
                    app = app.lower()
                if app == '}':
                    if len(buf) > 0:
                        # empty rule
                        if buf[-1] == '{':
                            x = 0
                            z = len(buf) - 2
                            while x == 0 and z >= 0:
                                if buf[z] == '{' or buf[z] == '}' or\
                                        buf[z] == ';' or (buf[z] == '/' and\
                                        buf[z-1] == '*'):
                                    x = z + 1
                                z -= 1
                            buf = buf[0:x]
                            out += buf
                            buf = ''
                            continue
                        # drop last semi-colon
                        elif buf[-1] == ';':
                            buf = buf[0:-1]
                    ruleEnd = True
                elif app == '-ms-filter' or app == 'filter:':
                    filter = True

                app = re.sub(ZERO_VALUES, '0', app)
                app = re.sub(SMALL_FLOATS, r'.\1\2', app)

                buf += app

                if filter and (buf[-1] == ')' or buf[-2] == ')'):
                    buf = re.sub(IEALPHA, r'\1alpha(opacity=\3)\4', buf)
                    filter = False

                #  #AABBCC
                if len(buf) >= 8 and buf[-1] != '"' and buf[-8] == '#':
                    lbuf = buf[-7:].lower()
                    if lbuf[0] == lbuf[1] and lbuf[2] == lbuf[3] and\
                            lbuf[4] == lbuf[5]:
                        c = lbuf[0] + lbuf[2] + lbuf[4] + buf[-1]
                        buf = buf[0:-7] + c

                # margin:0
                if buf[-15:-1] == 'margin:0 0 0 0':
                    buf = buf[0:-15] + 'margin:0' + buf[-1]
                elif buf[-13:-1] == 'margin:0 0 0':
                    buf = buf[0:-13] + 'margin:0' + buf[-1]
                elif buf[-11:-1] == 'margin:0 0':
                    buf = buf[0:-11] + 'margin:0' + buf[-1]
                # padding:0
                elif buf[-16:-1] == 'padding:0 0 0 0':
                    buf = buf[0:-16] + 'padding:0' + buf[-1]
                elif buf[-14:-1] == 'padding:0 0 0':
                    buf = buf[0:-14] + 'padding:0' + buf[-1]
                elif buf[-12:-1] == 'padding:0 0':
                    buf = buf[0:-12] + 'padding:0' + buf[-1]
                # border
                elif buf[-12:-1] == 'border:none':
                    buf = buf[0:-12] + 'border:0' + buf[-1]
                elif buf[-16:-1] == 'border-top:none':
                    buf = buf[0:-16] + 'border-top:0' + buf[-1]
                elif buf[-19:-1] == 'border-bottom:none':
                    buf = buf[0:-19] + 'border-bottom:0' + buf[-1]
                elif buf[-17:-1] == 'border-left:none':
                    buf = buf[0:-17] + 'border-left:0' + buf[-1]
                elif buf[-18:-1] == 'border-right:none':
                    buf = buf[0:-18] + 'border-right:0' + buf[-1]
                # outline
                elif buf[-13:-1] == 'outline:none':
                    buf = buf[0:-13] + 'outline:0' + buf[-1]
                # background
                elif buf[-16:-1] == 'background:none':
                    buf = buf[0:-16] + 'background:0' + buf[-1]
                # background-position
                elif buf[-28:-1] == 'background-position:0 0 0 0':
                    buf = buf[0:-28] + 'background-position:0 0' + buf[-1]
                # :first-letter and :first-line must be followed by a space
                elif buf[-14:-1] == ':first-letter'\
                        or buf[-12:-1] == ':first-line':
                    buf = buf[0:-1] + ' ' + buf[-1]

                if ruleEnd:
                    if bufferOutput:
                        out += buf
                    else:
                        sys.stdout.write(buf)
                    buf = ''
                    ruleEnd = False

    return out + buf


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            css = f.read()
    else:
        css = sys.stdin.read()
    m = minify(css, False)
