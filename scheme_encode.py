import codecs
import scheme
import argparse
import sys

f=None
if '--convert' in str(sys.argv):
    f = sys.stdout



def scheme_encode(input, errors='strict', filename='<data>', mode=0666):
    return (str(input), len(input))


First=True
lisp=['(begin \n']



def scheme_decode(input, errors='strict'):
    global First, lisp
    acc=['import scheme;scheme.jit.enabled=True;scheme.debug.setAll(0);'] if First else []
    First=False
    
    if not input: 
        if len(lisp)==1:
            return (u'', 0)
        return (u"",0)
    length = len(input)
    # Deal with chunked reading, where we don't get
    # data containing a complete line of source
    if not input.endswith('\n'):
        length = input.rfind('\n') + 1
    input = input[:length]
    
    
    lines = input.split('\n')
    fli = None
    for l in (x.rstrip().replace('++', '-=-1').replace('--','-=1') for x in lines):
        if l.endswith(';'):
            l = l[:-1]
        if l.strip().startswith('!'):
            if fli is None:
                fli = len(l) - len(l.lstrip())
            lisp.append(l.lstrip()[1:])
        elif l.strip()=='':
            lisp.append(l)
        else:
            if len(lisp) - lisp.count('')>1:
                lisp.append('\n)\n')
                acc.append(' '*(fli or 0) +'scheme.eval.Eval(%r)'%('\n'.join([lisp.pop(0) for i in range(len(lisp))])))
                fli = None
                lisp.append('(begin ')
            acc.append(l)
    if f: 
        f.write(u'\n'.join(acc)+'\n')
        return u'exit()\n', length
    return (u'\n'.join(acc)+'\n', length)

class Codec(codecs.Codec):
    def encode(self, input, errors='strict'):
        return scheme_encode(input, errors)
    def decode(self, input, errors='strict'):
        return scheme_decode(input, errors)

class StreamWriter(Codec, codecs.StreamWriter):
    pass

class StreamReader(Codec, codecs.StreamReader):
    pass

def getregentry():
    return codecs.CodecInfo(
        name='listp',
        encode=scheme_encode,
        decode=scheme_decode,
#        incrementalencoder=IncrementalEncoder,
#        incrementaldecoder=IncrementalDecoder,
        streamreader=StreamReader,
        streamwriter=StreamWriter,
    )
