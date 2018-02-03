import sys

#checks the specific syntax for the CP forensics questions, and can handle multiple answers
def check(args, debug=False):

    if (len(args) < 2):
        return TypeError("Not Enough Arguments")

    filepath = args[0]
    answers = args[1:]

    count = 0
    for ans in answers:
        if debug:
            print "Using filepath:", filepath
        file = open(filepath, 'r')
        for line in file.read().split('\n'):
            if line[:7] == "ANSWER:":
                if ans.lower() in line[7:].lower(): # case insensitive
                    count = count + 1
    if count == len(answers): return True # if all are answered
    return False
