from modules.FileContents import check

filename = "tests/sshd_config"

def test_BasicContains():
    assert check([filename, "true", "AddressFamily any"], True)
    assert not check([filename, "true", "AddressFamily none"])
    assert check([filename, "false", "AddressFamily none"])
    assert not check([filename, "false", "AddressFamily any"])

def test_RegexMatching():
    assert check([filename, "true", "#\s?Port 22"])
    assert check([filename, "true", "^UsePAM yes"])
