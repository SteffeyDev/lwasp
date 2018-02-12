import subprocess

#check if updates are installed for a specific service
def check(args, debug=False):

    if (len(args) < 2):
        raise TypeError("Not Enough Arguments")

    serviceName = args[0]
    mode = args[1].lower()

    if mode == "updated":
        if (len(args) < 3):
            raise TypeError("Missing Update Version")
        version = args[2]
        cmd = 'dpkg -l ' + serviceName + ' | grep -E \"^ii\" | tr -s \' \' | cut -d\' \' -f3'
        process = subprocess.Popen(cmd, shell=True, executable="/bin/bash", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output,error = process.communicate()
        if process.returncode != 0:
            return False
        if version in output:
            return True
    elif mode == "installed":
        cmd = 'dpkg -l ' + serviceName
        process = subprocess.Popen(['dpkg', '-l', serviceName], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.communicate()
        return process.returncode == 0
    else:
        raise TypeError("Package mode must be 'updated' or 'installed'")

    return False

