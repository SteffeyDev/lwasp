import subprocess
import sys

#generic command analysis for output, allowing greater flexibility
def check(args, debug=False):

    if (len(args) < 3):
        raise TypeError("Not Enough Arguments")

    command = args[0]
    should = args[1].lower() == "true"
    content = args[2]

    output, err = subprocess.Popen(command.split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE).communicate()
    shortOutput = ' '.join(output.split()).decode('utf-8')
    shortErr = ' '.join(err.split()).decode('utf-8')
    if debug:
        print "Command Output:", shortOutput
    if content in shortOutput or content in shortErr:
        return should
    return not should
