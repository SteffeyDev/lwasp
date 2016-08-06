
def add(array, line):
    if line in array:
        array.remove(line)
    else:
        array.append(line)
