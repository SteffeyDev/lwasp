import subprocess

#check if updates are installed for a specific service
def check(args):

    if (len(args) < 2):
        raise TypeError("Not Enough Arguments")

    serviceName = args[0]
    version = args[1]

    cmd = 'dpkg -l ' + serviceName + ' | grep -E \"^ii\" | tr -s \' \' | cut -d\' \' -f3'
    output,error = subprocess.Popen(cmd, shell=True, executable="/bin/bash", stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    if version in output:
        return True
    return False

