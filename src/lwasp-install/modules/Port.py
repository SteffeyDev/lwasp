import subprocess
import sys
import re

#checks whether a port is open
def check(args, debug=False):

    if (len(args) < 2):
        raise TypeError("Not Enough Arguments")

    mode = args[1]
    if (mode != "listening" and mode != "established"):
        raise TypeError("Second parameter must be 'listening' or 'established'")

    port = args[0]
    portNumber = None
    try:
        portNumber = int(args[0])
    except:
        with open('/etc/services', 'r') as file:
            for line in file.read().split('\n'):
                m = re.match('(\w+)\s+(\d+)/(udp|tcp).*', line)
                if m is not None and m.group(1) == port:
                    portNumber = int(m.group(2))

    output = subprocess.check_output(['sudo','netstat','-tunelp'])
    lines = output.split('\n')
    for line in lines:
        if ':' + str(portNumber) in line and ((mode == 'listening' and 'LISTEN' in line) or (mode == 'established' and 'ESTABLISHED' in line)):
            return True
    return False 
