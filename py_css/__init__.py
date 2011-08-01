#!/usr/bin/env python

import sys
from optparse import OptionParser
from py_css.token import *

UNITS = set(('px', 'em', 'pt', 'in', 'cm', 'mm', 'pc', 'ex'))
IEALPHA = 'progid:dximagetransform.microsoft.alpha(opacity='

def minify(s, bufferOutput=True, debug=False):
    """Minify a string of CSS."""
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

    if not bufferOutput and debug: bufferOutput = True

    for c in s:
        if comment:
            tmp += c
            if c == '/' and tmp[-2] == '*':
                if tmp[-3] == '\\': # ie5mac hack
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

        # todo should separate these for stuff like "don't"
        if quote or squote:
            buf += c
            if ((quote and c == '"') or (squote and c == "'")) and buf[-2] != '\\':
                quote = False
                squote = False
                if filter and buf[-2] == ')':
                    x = buf.lower().find(IEALPHA)
                    if x >= 0:
                        y = x + len(IEALPHA)
                        buf = buf[0:x] + 'alpha(opacity=' + buf[y:]
                    filter = False
            continue

        app = ''
        token = tokenize(c)

        if token == Whitespace:
            if rgb:
                if tmp:
                    app += '%02x' % int(tmp[0:-1])
                tmp = ''
            else:
                if not boundary:
                    app = ' '
                if tmp:
                    app += tmp
                    if app[-1] != '/':
                        boundary = False
                tmp = ''
                space = True
        elif token == Slash:
            if not boundary and tmp:
                app += ' '
            boundary = True
            space = False
            tmp += c
        elif token == Star:
            if tmp == '/' and (not buf or buf[-1] != '>'):
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
        elif token == Period:
            if not rule:
                if (space and not boundary) or (tmp and (not buf or buf[-1] != '.')):
                    app += ' '
                boundary = True
                app += tmp
                app += c
                tmp = ''
            else:
                tmp += c
            space = False
        elif token == Hyphen:
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
            if not boundary and tmp: app += ' '
            boundary = True
            space = False
            rule = True
            app += tmp
            app += c
            tmp = ''
        elif token == RightBrace:
            if not boundary and tmp: app += ' '
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
            if rgb:
                app += '%02x' % int(tmp)
            else:
                if not boundary: app += ' '
                app += tmp
                app += c
            tmp = ''
            boundary = True
            space = False
        elif token == SemiColon:
            if not boundary: app += ' '
            boundary = True
            Space = False
            if skip:
                skip = False
            else:
                if rgb:
                    app += '%02x' % int(tmp[0:-1])
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
        elif token == Bang:
            boundary = True
            tmp += c
        else:
            tmp += c
            space = False

        if app:
            #print "> " + app
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
                if rule and app[-1] != '{' and buf[-1] != '(':
                    app = app.lower()
                if app == '}':
                    if buf:
                        # empty rule
                        if buf[-1] == '{':
                            x = 0
                            z = len(buf) - 2
                            while x == 0 and z >= 0:
                                if (buf[z] == '{' or buf[z] == '}' or
                                        buf[z] == ';' or (buf[z] == '/' and
                                        buf[z-1] == '*')):
                                    x = z + 1
                                z -= 1
                            buf = buf[0:x]
                            if debug: print "{0:10}  |  {1:50}  |  {2:20}".format('empty rule', out, buf)
                            if bufferOutput:
                                out += buf
                            else:
                                if not debug: sys.stdout.write(buf)
                            buf = ''
                            continue
                        # drop last semi-colon
                        elif buf[-1] == ';':
                            buf = buf[0:-1]
                    ruleEnd = True
                elif app == '-ms-filter:' or app == 'filter:':
                    filter = True

                # zero values
                app_len = len(app)
                if (app_len >= 2 and app[0] == '0' and
                        (app[1:3] in UNITS or app[1] == '%')):
                    if app[-1] == ';':
                        app = '0;'
                    elif app[-1] == ',':
                        app = '0,'
                    else:
                        app = '0'
                elif (app_len >= 3 and app[0:2] == ' 0' and (app[2] == '%' or
                        app_len >= 4 and app[2:4] in UNITS)):
                    if app[-1] == ';':
                        app = ' 0;'
                    elif app[-1] == ',':
                        app = ' 0,'
                    else:
                        app = ' 0'
                # small floats
                elif app_len >= 3 and app[0:2] == '0.':
                    app = app[1:]
                elif app_len >= 4 and app[0:3] == ' 0.':
                    app = ' ' + app[2:]

                #  #AABBCC
                if len(app) == 7 and app[0] == '#':
                    la = app.lower();
                    if la[1] == la[2] and la[3] == la[4] and la[5] == la[6]:
                        app = app[0] + la[1] + la[3] + la[5]

                buf += app

                if filter and (buf[-1] == ')' or buf[-2] == ')'):
                    x = buf.lower().find(IEALPHA)
                    if x >= 0:
                        y = x + len(IEALPHA)
                        buf = buf[0:x] + 'alpha(opacity=' + buf[y:]
                    filter = False

                #  #AABBCC
                if len(buf) >= 8 and buf[-1] != '"' and buf[-8] == '#':
                    lbuf = buf[-7:].lower()
                    if (lbuf[0] == lbuf[1] and lbuf[2] == lbuf[3] and
                            lbuf[4] == lbuf[5]):
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
                    if debug: print "{0:10}  |  {1:50}  |  {2:20}".format('rule end', out, buf)
                    if bufferOutput:
                        out += buf
                    else:
                        if not debug: sys.stdout.write(buf)
                    buf = ''
                    ruleEnd = False

    if debug: print "{0:10}  |  {1:50}  |  {2:20}".format('eof', out, buf)
    if not bufferOutput:
        if not debug: sys.stdout.write(buf)
    else:
        return out + buf

def streamer(f):
    for line in f:
        for token in line:
            yield token

def main():
    parser = OptionParser()
    parser.add_option("-d", "--debug",
                      action="store_true", dest="debug", default=False,
                      help="print debugging messages")
    (options, args) = parser.parse_args()
    if len(args) >= 1:
        for filename in args:
            with open(filename, 'r') as f:
                css = streamer(f)
                minify(css, False, options.debug)
    else:
        css = streamer(sys.stdin)
        minify(css, False, options.debug)

if __name__ == "__main__":
    main()
