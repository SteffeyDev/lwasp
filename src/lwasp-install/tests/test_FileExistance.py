from modules.FileExistance import check

filepath_exists = "tests/sshd_config"
filepath_notexists = "tests/random_file"

def test_FileExistance():
    assert check([filepath_exists])
    assert not check([filepath_notexists])

def test_DirectoryExistance():
    assert check(["tests"])
    assert not check(["bla"])
