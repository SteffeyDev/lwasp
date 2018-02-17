import os

#check if a file exists at a given filepath using os.path
def check(args, debug=False):
    
    if (len(args) < 1):
        raise TypeError("Not Enough Arguments")

    filepath = args[0]

    if debug:
        print "Using Filepath: " + filepath

    return os.path.isfile(filepath) or os.path.isdir(filepath)
