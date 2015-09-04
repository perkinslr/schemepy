__author__ = 'perkins'

DEBUG = False

debug_settings={ 
  'pushStack':False,        #watch increases in stack depth
  'popStack':False,         #watch decreses in stack depth
  'discardedFraames':False, #save discarded frames, memory leak!!!
  'repl':False,             #prints more information on exceptions in the repl
  'syntax':False,           #prints informtion when doing syntax
  'symbols':False,          #prints line numbers in symbols' repr
  'patternMatcher':False,   #prints information when matching symbols
  'tracebck':False          #returns extra informtion in ReportProcesser on errors
}

def getDebug(key):
    if key in debug_settings:
      return debug_settings[key]
    return False

setDebug=debug_settings.__setitem__


def LOG(SECTION, *args):
    if not getDebug(SECTION):
        return
    print SECTION,
    for arg in args:
        print arg,
    print


