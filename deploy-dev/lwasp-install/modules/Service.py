#checks if a service is running using the bash command ps -A
def check(args):

    if (len(args) < 2):
        raise TypeError("Not Enough Arguments")

    serviceName = args[0]
    shouldBe = args[1].lower() == "true"

    output = subprocess.check_output(['ps', '-A'])
    if serviceName in output: return shouldBe
    return not shouldBe

