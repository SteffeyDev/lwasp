import sys

#checks the specific syntax for the CP forensics questions, and can handle multiple answers
def check(args, debug=False):

    if (len(args) < 2):
        return TypeError("Not Enough Arguments")

    filepath = args[0]
    answers_needed = [ str.lower() for str in args[1:] ]

    answers_provided = []
    file = open(filepath, 'r')
    for line in file.read().split('\n'):
        if line[:7] == "ANSWER:":
            answers_provided.append(line[7:].lower().lstrip())

    if debug:
        print "Answers needed:", set(answers_needed)
        print "Answers provided:", set(answers_provided)

    return set(answers_needed) == set(answers_provided)
