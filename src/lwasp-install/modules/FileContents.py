import os
import codecs
import string
from os.path import expanduser
import sys
import re

#method to check the file to see if it contains all or none of the strings in the array of contents
def check(args, debug=False):

    if (len(args) < 3):
        raise TypeError("Not Enough Arguments")

    filepath = args[0]
    mode = args[1].lower() == "true"
    contents = args[2:]

    inFile = codecs.open(string.replace(filepath, '~', expanduser("~")),'r','utf-8') # open(string.replace(filepath, '~', expanduser("~")), 'r') # if ~ exists in string, replace it with the user's home directory absolute path
    text = inFile.read()
    text_list = [' '.join(line.split()) for line in text.split('\n')]
    inFile.close()

    patterns = [re.compile(pattern) for pattern in contents]

    if debug:
        print "Using file path: " + string.replace(filepath, '~', expanduser("~"))

    for pattern in patterns:
        
        pattern_found = False
        for line in text_list:
            if debug:
                print "Looking for pattern:", pattern.pattern, ", on line:", line
            result = pattern.search(line)
            if result is not None:
                pattern_found = True

        if pattern_found != mode:
            return False

    return True
