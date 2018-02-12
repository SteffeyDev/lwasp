import subprocess

#checks if a service is running using the bash command ps -A
def check(args, debug=False):

    if (len(args) < 3):
        raise TypeError("Not Enough Arguments")

    serviceName = args[0]
    shouldBe = args[1].lower() == "true"
    mode = args[2].lower()

    step1 = subprocess.Popen(['service', serviceName, 'status'], stdout=subprocess.PIPE)
    if mode == "active":
        output = subprocess.check_output(['grep', 'Active'], stdin=step1.stdout)
        if 'Active: active' in output:
            return shouldBe
        return not shouldBe
    elif mode == "loaded":
        output = subprocess.check_output(['grep', 'Loaded'], stdin=step1.stdout)
        if 'Loaded: loaded' in output:
            return shouldBe
        return not shouldBe
    else:
        raise TypeError("Service mode must be 'active' or 'loaded'")
