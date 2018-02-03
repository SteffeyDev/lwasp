import os

#check if a file exists at a given filepath using os.path
def check(args, debug=False):
    
    if (len(args) < 2):
        raise TypeError("Not Enough Arguments")

    filepath = args[0]
    should = args[1].lower() == "true"

    if debug:
        print "Using Filepath: " + filepath
    if os.path.isfile(filepath) or os.path.isdir(filepath): return should
    return not should
