import os
import socket
import unittest

from run import is_port_in_use, is_process_running


class TestRunLauncher(unittest.TestCase):
    def test_is_port_in_use_detects_bound_socket(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
            sock.close()
            self.assertFalse(is_port_in_use(port))

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as other:
                other.bind(("127.0.0.1", port))
                self.assertTrue(is_port_in_use(port))

    def test_is_process_running_for_current_pid(self):
        self.assertTrue(is_process_running(os.getpid()))


if __name__ == "__main__":
    unittest.main()
