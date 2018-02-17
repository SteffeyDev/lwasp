from modules.Port import check
import socket
import mock

netstat_output = 'tcp\t0\t0 127.0.0.1:80\t\t0.0.0.0:*\tLISTEN\ntcp\t0\t0 127.0.0.1:22\t\t0.0.0.0:*\tESTABLISHED\ntcp\t0\t0 127.0.0.1:443\t\t0.0.0.0:*\tLISTEN'

@mock.patch('subprocess.check_output')
def test_CheckPortListening(mock_subproc_check):
    mock_subproc_check.return_value = netstat_output
    assert check(['443', 'listening'])
    assert check(['https', 'listening'])

@mock.patch('subprocess.check_output')
def test_CheckPortEstablished(mock_subproc_check):
    mock_subproc_check.return_value = netstat_output
    assert check(['22', 'established'])
    assert check(['ssh', 'established'])

