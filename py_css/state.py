class State:
    def __init__(self):
        self.boundary = True
        self.charset = False
        self.comment = False
        self.skip = False
        self.rgb = False
        self.quote = False
        self.squote = False
        self.ie5mac = False
        self.filter = False
        self.space = False
        self.media = False
        self.rule = False
        self.ruleEnd = False

        self._buffer = ''#[]
        self._append = ''#[]
        self._tmp = ''#[]

        #self._b = None
        #self._a = None
        #self._t = None

    def __str__(self):
        arr = []
        arr.append('B' if self.boundary else 'b')
        arr.append('A' if self.charset else 'a')
        arr.append('C' if self.comment else 'c')
        arr.append('-' if self.skip else '_')
        arr.append('G' if self.rgb else 'g')
        arr.append('Q' if self.quote else 'q')
        arr.append('S' if self.squote else 's')
        arr.append('I' if self.ie5mac else 'i')
        arr.append('F' if self.filter else 'f')
        arr.append('S' if self.space else 's')
        arr.append('M' if self.media else 'm')
        arr.append('R' if self.rule else 'r')
        arr.append('N' if self.ruleEnd else 'n')
        return ''.join(arr)

    def append(self, s):
        if s:
            #self._append.append(s)
            self._append += s
        #self._a = None
        return self

    def set_append(self, s):
        self._append = s#[]
        #return self.append(s)
        return self

    def buffer(self, s):
        #self._buffer.append(s)
        #self._b = None
        self._buffer += s
        return self

    def set_buffer(self, s):
        self._buffer = s#[]
        #return self.buffer(s)
        return self

    def hold(self, s):
        #self._tmp.append(s)
        #self._t = None
        self._tmp += s
        return self

    def clear(self):
        self._tmp = ''#[]
        #self._t = None
        return self

    def clear_buffer(self):
        self._buffer = ''#[]
        #self._b = None
        return self

    def ready(self, s):
        #self._append.extend(self._tmp)
        #return self.append(s).clear()
        self._append += self._tmp
        if s:
            self._append += s
        self._tmp = ''
        return self

    def get_buffer(self):
        #if self._b is None:
        #    self._b = ''.join(self._buffer)
        #return self._b
        return self._buffer

    def get_append(self):
        #if self._a is None:
        #    self._a = ''.join(self._append)
        #return self._a
        return self._append

    def get_tmp(self):
        #if self._t is None:
        #    self._t = ''.join(self._tmp)
        #return self._t
        return self._tmp
