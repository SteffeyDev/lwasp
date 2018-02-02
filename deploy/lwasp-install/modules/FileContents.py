import os
import codecs
import string
from os.path import expanduser
import sys

#method to check the file to see if it contains all or none of the strings in the array of contents
def check(args):

    if (len(args) < 3):
        raise TypeError("Not Enough Arguments")

    filepath = args[0]
    mode = args[1].lower() == "true"
    contents = args[2:]

    inFile = codecs.open(string.replace(filepath, '~', expanduser("~")),'r','utf-8') # open(string.replace(filepath, '~', expanduser("~")), 'r') # if ~ exists in string, replace it with the user's home directory absolute path
    text = inFile.read()
    text = string.replace(text, "\n", "(<^>]")
    text = ' '.join(text.split())
    text = string.replace(text, "\"", "")
    text_list = text.split("(<^>]")
    inFile.close()

    should_return = not mode

    for contains in contents:
        if debug:
            print "Using file path: " + string.replace(filepath, '~', expanduser("~"))

        contains = string.replace(contains, "\"", "")
        contains = ' '.join(contains.split())
        contains_pieces = contains.split("~")

        if debug:
            print "Looking for text:", contains
            print "File text:", text

        for line in text_list:
            if contains_pieces[0] in line:
                if len(contains_pieces) == 2:
                    if contains_pieces[1] in line and not isCommented(line, filepath):
                        should_return = mode
                elif not isCommented(line, filepath):
                    should_return = mode

    return should_return

def isCommented(line, filename):
    return (".conf" in filename or ".gsettings" in filename) and line.find("#") == 0

