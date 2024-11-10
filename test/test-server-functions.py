import unittest
from unittest.mock import Mock, patch, MagicMock
import os
import json

from server.functions import request_file, receive_file, send_file  # Adjust the import as necessary


class TestFileTransferFunctions(unittest.TestCase):

    @patch('database.connect.Files')
    def test_request_file(self, mock_files):
        mock_client1 = Mock()
        mock_client2 = Mock()
        clients = [mock_client1, mock_client2]
        filename = "test_file.txt"

        request_file(clients, filename)

        request_data = json.dumps({"type": "request", "filename": filename}).encode('utf-8')
        mock_client1.sendall.assert_called_once_with(request_data)
        mock_client2.sendall.assert_called_once_with(request_data)

    @patch('database.connect.Files.get_by_name')
    @patch('database.connect.Files.update_uploaded_status')
    def test_receive_file_success(self, mock_get_by_name, mock_update_uploaded_status):
        mock_conn = Mock()
        mock_session = MagicMock()
        mock_get_by_name.return_value = MagicMock(id=1)  # Simulate a file found in the database

        # Simulate file data transmission
        mock_conn.recv.side_effect = [b'This is a test.', b' More data.', b'']
        filename = "received_file.txt"

        # Call the function
        receive_file(mock_conn, filename, session=mock_session)

        # Check if receive logic was called
        mock_conn.recv.assert_called()
        mock_get_by_name.assert_called_once_with(mock_session, filename)
        mock_update_uploaded_status.assert_called_once_with(mock_session, 1, True)

        # Verify file contents
        with open(os.path.join("uploads", filename), "rb") as f:
            content = f.read()
            self.assertEqual(content, b'This is a test. More data.')

        # Clean up
        os.remove(os.path.join("uploads", filename))

    @patch('database.connect.Files')
    def test_receive_file_empty_filename(self, mock_files):
        mock_conn = Mock()
        mock_session = MagicMock()
        with patch('builtins.print') as mock_print:
            receive_file(mock_conn, "", session=mock_session)
            mock_print.assert_called_with("[ERROR] filename cannot be empty")

    @patch('database.connect.Files.get_by_name')
    def test_send_file_success(self, mock_get_by_name):
        mock_conn = Mock()
        mock_session = MagicMock()
        mock_get_by_name.return_value = MagicMock(id=1)

        filename = "test_file.txt"
        # Create a temporary file to simulate sending
        with open(os.path.join("uploads", filename), "wb") as f:
            f.write(b'This is some test data.')

        send_file(mock_conn, filename, session=mock_session)

        mock_get_by_name.assert_called_once_with(mock_session, filename)

        # Check that data was sent in chunks as expected
        with open(os.path.join("uploads", filename), "rb") as f:
            content = f.read()
            mock_conn.sendall.assert_any_call(content)

        # Clean up
        os.remove(os.path.join("uploads", filename))

    @patch('database.connect.Files.get_by_name')
    def test_send_file_not_found(self, mock_get_by_name):
        mock_conn = Mock()
        mock_session = MagicMock()
        mock_get_by_name.return_value = None

        with patch('builtins.print') as mock_print:
            send_file(mock_conn, "non_existing_file.txt", session=mock_session)
            mock_print.assert_called_with("[ERROR] file not found")

    @patch('database.connect.Files.get_by_name')
    def test_send_file_exception(self, mock_get_by_name):
        mock_conn = Mock()
        mock_session = MagicMock()
        mock_get_by_name.return_value = MagicMock(id=1)

        filename = "test_file.txt"
        # Create a temporary file to simulate sending
        with open(os.path.join("uploads", filename), "wb") as f:
            f.write(b'This is some test data.')

        mock_conn.sendall.side_effect = Exception("Connection lost")

        with patch('builtins.print') as mock_print:
            send_file(mock_conn, filename, session=mock_session)
            mock_print.assert_called_with("[ERROR] file sending error: Connection lost")

        # Clean up
        os.remove(os.path.join("uploads", filename))


if __name__ == "__main__":
    unittest.main()
