import subprocess
import sys

#checks whether a port is open
def check(args, debug=False):

    if (len(args) < 2):
        raise TypeError("Not Enough Arguments")

    port = args[0]
    open = args[1].lower() == "true"

    output = subprocess.check_output(['sudo','netstat','-tunelp'])
    lines = output.split('\n')
    for line in lines:
        if ':' + port in line and 'LISTEN' in line:
            return open
    return not open
