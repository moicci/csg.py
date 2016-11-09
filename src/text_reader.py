# coding: utf-8
#

class TextReader:

    def __init__(self, filename):
        self.line = 0
        self.io = open(filename)
    
    def __iter__(self):
        # next()はselfが実装してるのでそのままselfを返す
        return self

    # iterator として使うため、１行ずつ返す
    def next(self):
        line = self.readline()
        #if not line:
        if line == None:
            raise StopIteration()
        return line

    def close(self):
        if self.io:
            self.io.close()
            self.io = None

    def readline(self, chop=True):
        self.line += 1
        line = self.io.readline()

        # EOF では None でなく空が返るらしい
        if line == "":
            return None

        if chop:
            line = line.rstrip("\n")
        #print "%d: '%s'" % (self.line, line)
        return line

