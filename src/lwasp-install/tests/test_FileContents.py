from modules.FileContents import check

filename = "tests/sshd_config"

def test_BasicContains():
    assert check([filename, "true", "AddressFamily any"])
    assert not check([filename, "true", "AddressFamily none"])
    assert check([filename, "false", "AddressFamily none"])
    assert not check([filename, "false", "AddressFamily any"])

def test_RegexMatching():
    assert check([filename, "true", "#\s?Port 22"])
    assert check([filename, "true", "^UsePAM yes$"])
    assert check([filename, "false", "^UseDNS no$"])

def test_Multiple():
    assert check([filename, "true", "^PasswordAuthentication no", "^PubkeyAuthentication yes"])
    assert check([filename, "false", "^PermitTTY yes", "^AllowTCPForwarding yes"])
    assert not check([filename, "true", "^PasswordAuthentication no", "^PermitTTY yes"])
    assert not check([filename, "false", "^AllowTCPForwarding yes", "^PubkeyAuthentication yes"])

def test_AdvancedRegex():
    assert check([filename, "true", "^Banner [a-z/._]"])
    assert check([filename, "true", "^MaxAuthTries [0-3]"])
    assert check([filename, "false", "^LogLevel (DEBUG|TRACE|FATAL)"])
