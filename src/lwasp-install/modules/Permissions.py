import sys
import os
import stat

#checks the permissions on a file and returns false if any of the permissions don't match - need to simplify
def check(args, debug=False):

    if (len(args) < 2):
        raise TypeError("Not Enough Arguments")

    filepath = args[0]
    permissions = [int(perm) for perm in args[1:] ]

    current = int(oct(os.stat(filepath)[stat.ST_MODE])[-3:])
    return current in permissions
