#!/usr/bin/env python

import sys
from optparse import OptionParser
from py_css.token import tokenize
from py_css.state import State

UNITS = set(('px', 'em', 'pt', 'in', 'cm', 'mm', 'pc', 'ex'))
IEALPHA = 'progid:dximagetransform.microsoft.alpha(opacity='

def minify(s, bufferOutput=True, debug=False):
    """Minify a string of CSS."""
    out = ''

    state = State()

    if not bufferOutput and debug: bufferOutput = True

    for c in s:
        if state.comment:
            state.hold(c)
            tmp = state.get_tmp()
            if c == '/' and tmp[-2] == '*':
                if tmp[-3] == '\\': # ie5mac hack
                    state.buffer('/*\\*/')
                    state.ie5mac = True
                elif state.ie5mac:
                    state.buffer('/**/')
                    state.ie5mac = False
                elif tmp[2] == '!': # important comments
                    state.buffer(tmp)
                state.clear()
                state.comment = False
            continue

        # todo should separate these for stuff like "don't"
        if state.quote or state.squote:
            state.buffer(c)
            if (((state.quote and c == '"') or (state.squote and c == "'"))
                    and state.get_buffer()[-2] != '\\'):
                state.quote = False
                state.squote = False
                buf = state.get_buffer()
                if state.filter and buf[-2] == ')':
                    x = buf.lower().find(IEALPHA)
                    if x >= 0:
                        y = x + len(IEALPHA)
                        state.set_buffer(buf[:x]).buffer('alpha(opacity=').buffer(buf[y:])
                    state.filter = False
            continue

        state.set_append('')
        token = tokenize(c)
        token.process(state, c)

        app = state.get_append()
        foo = app
        buf = state.get_buffer()
        if app:
            if app == '@charset':
                if state.charset:
                    state.skip = True
                else:
                    state.charset = True
                    state.buffer(app)
            elif app == ' rgb(':
                state.rgb = True
                state.buffer(' #')
            elif app == 'rgb(':
                state.rgb = True
                state.buffer('#')
            elif not state.skip:
                if state.rule and app[-1] != '{':
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
                            buf = buf[:x]
                            if debug: print "{:13} {:10}  |  {:50}  |  {:20}".format(state, 'empty rule', out, buf)
                            if bufferOutput:
                                out += buf
                            else:
                                if not debug: sys.stdout.write(buf)
                            state.set_buffer('')
                            continue
                        # drop last semi-colon
                        elif buf[-1] == ';':
                            buf = buf[:-1]
                    state.ruleEnd = True
                elif app == '-ms-filter:' or app == 'filter:':
                    state.filter = True

                # zero values
                app_len = len(app)
                if (app_len >= 2 and app[0] == '0' and
                        (app[1:3] in UNITS or app[1] == '%')):
                    if app[-1] == ';':
                        app = '0;'
                    else:
                        app = '0'
                elif (app_len >= 3 and app[:2] == ' 0' and (app[2] == '%' or
                        app_len >= 4 and app[2:4] in UNITS)):
                    if app[-1] == ';':
                        app = ' 0;'
                    else:
                        app = ' 0'
                # small floats
                elif app_len >= 3 and app[:2] == '0.':
                    app = app[1:]
                elif app_len >= 4 and app[:3] == ' 0.':
                    app = ' ' + app[2:]

                if debug: print "{:13} {:10}|{:50}|{:20}|{}|".format(state, 'append', out, buf, app)
                state.set_buffer(buf).buffer(app)
                buf = state.get_buffer()

                if state.filter and (buf[-1] == ')' or buf[-2] == ')'):
                    x = buf.lower().find(IEALPHA)
                    if x >= 0:
                        y = x + len(IEALPHA)
                        state.set_buffer(buf[:x]).buffer('alpha(opacity=').buffer(buf[y:])
                        buf = state.get_buffer()
                    state.filter = False

                #  #AABBCC
                if len(buf) >= 8 and buf[-1] != '"' and buf[-8] == '#':
                    lbuf = buf[-7:].lower()
                    if (lbuf[0] == lbuf[1] and lbuf[2] == lbuf[3] and
                            lbuf[4] == lbuf[5]):
                        state.clear_buffer().buffer(buf[:-7]).buffer(lbuf[0])\
                                .buffer(lbuf[2]).buffer(lbuf[4]).buffer(buf[-1])
                        buf = state.get_buffer()

                # margin:0
                if buf[-15:-1] == 'margin:0 0 0 0':
                    state.set_buffer(buf[:-15]).buffer('margin:0').buffer(buf[-1])
                elif buf[-13:-1] == 'margin:0 0 0':
                    state.set_buffer(buf[:-13]).buffer('margin:0').buffer(buf[-1])
                elif buf[-11:-1] == 'margin:0 0':
                    state.set_buffer(buf[:-11]).buffer('margin:0').buffer(buf[-1])
                # padding:0
                elif buf[-16:-1] == 'padding:0 0 0 0':
                    state.set_buffer(buf[:-16]).buffer('padding:0').buffer(buf[-1])
                elif buf[-14:-1] == 'padding:0 0 0':
                    state.set_buffer(buf[:-14]).buffer('padding:0').buffer(buf[-1])
                elif buf[-12:-1] == 'padding:0 0':
                    state.set_buffer(buf[:-12]).buffer('padding:0').buffer(buf[-1])
                # border
                elif buf[-12:-1] == 'border:none':
                    state.set_buffer(buf[:-12]).buffer('border:0').buffer(buf[-1])
                elif buf[-16:-1] == 'border-top:none':
                    state.set_buffer(buf[:-16]).buffer('border-top:0').buffer(buf[-1])
                elif buf[-19:-1] == 'border-bottom:none':
                    state.set_buffer(buf[:-19]).buffer('border-bottom:0').buffer(buf[-1])
                elif buf[-17:-1] == 'border-left:none':
                    state.set_buffer(buf[:-17]).buffer('border-left:0').buffer(buf[-1])
                elif buf[-18:-1] == 'border-right:none':
                    state.set_buffer(buf[:-18]).buffer('border-right:0').buffer(buf[-1])
                # outline
                elif buf[-13:-1] == 'outline:none':
                    state.set_buffer(buf[:-13]).buffer('outline:0').buffer(buf[-1])
                # background
                elif buf[-16:-1] == 'background:none':
                    state.set_buffer(buf[:-16]).buffer('background:0').buffer(buf[-1])
                # background-position
                elif buf[-28:-1] == 'background-position:0 0 0 0':
                    state.set_buffer(buf[:-28]).buffer('background-position:0 0').buffer(buf[-1])
                # :first-letter and :first-line must be followed by a space
                elif buf[-14:-1] == ':first-letter'\
                        or buf[-12:-1] == ':first-line':
                    state.set_buffer(buf[:-1]).buffer(' ').buffer(buf[-1])

                if state.ruleEnd:
                    buf = state.get_buffer()
                    if debug: print "{:13} {:10}|{:50}|{:20}".format(state, 'rule end', out, buf)
                    if bufferOutput:
                        out += buf
                    elif not debug:
                        sys.stdout.write(buf)
                    state.set_buffer('')
                    state.ruleEnd = False

    buf = state.get_buffer()
    if debug: print "{:13} {:10}|{:50}|{:20}".format(state, 'eof', out, buf)
    if bufferOutput:
        return out + buf
    if not debug:
        sys.stdout.write(buf)

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
