from modules.Forensics import check

filepath = "tests/Forensics1.txt"
filepath2 = "tests/Forensics2.txt"

def test_MultipleAnswers():
    assert check([filepath, "This is an answer", "/answer/that/is/filepath.log"])
    assert not check([filepath, "This is an answer"])
    assert not check([filepath, "/answer/that/is/filepath.log"])

def test_SingleAnswer():
    assert check([filepath2, "Single Answer"])
    assert not check([filepath2, "Double Answer"])
