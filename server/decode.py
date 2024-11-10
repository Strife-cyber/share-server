import json
import socket
import threading
from database.connect import Files, session
from server.functions import request_file, send_file, receive_file

def setup_transfer_socket() -> tuple:
    """Sets up a transfer socket and returns the socket and the assigned port."""
    transfer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transfer_socket.bind(('', 0))  # Bind to an available port
    transfer_socket.listen(1)
    transfer_port = transfer_socket.getsockname()[1]
    return transfer_socket, transfer_port

def start_transfer_thread(transfer_socket, filename, transfer_session, operation):
    """
    Starts a new thread for handling file transfer.
    :param transfer_socket: The socket used for file transfer.
    :param filename: The name of the file to send or receive.
    :param transfer_session: The database session.
    :param operation: The file operation function (send_file or receive_file).
    """
    def handle_transfer():
        try:
            client_socket, _ = transfer_socket.accept()
            operation(client_socket, filename, session=transfer_session)
        finally:
            transfer_socket.close()

    threading.Thread(target=handle_transfer, daemon=True).start()

def create_response(status, message, filename, transfer_port=None):
    """
    Creates a response dictionary.
    :param status: Status of the response.
    :param message: Message to send in the response.
    :param filename: Name of the file involved in the transfer.
    :param transfer_port: Port for file transfer, if applicable.
    :return: Response dictionary.
    """
    response = {
        "status": status,
        "message": message,
        "filename": filename
    }
    if transfer_port:
        response["transfer_port"] = transfer_port
    return response

def decode(json_data, conn: socket.socket, clients) -> None:
    """
    Decodes a request and processes it.
    :param json_data: The JSON data from the client request.
    :param conn: The main client connection socket.
    :param clients: The list of all connected client sockets.
    :return: None
    """
    try:
        request = json.loads(json_data)
        request_type = request.get("type")
        filename = request.get("filename")

        if not filename:
            response = create_response("error", "Filename missing in request.", "")
        else:
            # Handle file request
            if request_type == "request":
                file = Files.get_by_name(session, filename)
                if not file or not json.loads(file.destructure()).get('uploaded'):
                    Files.create(session, filename)
                    request_file(clients, filename)
                    response = create_response("pending", f"Requesting {filename} from peers.", filename)
                else:
                    transfer_socket, transfer_port = setup_transfer_socket()
                    response = create_response("ready", f"{filename} is ready for download.", filename, transfer_port)
                    start_transfer_thread(transfer_socket, filename, session, send_file)

            # Handle file upload
            elif request_type == "upload":
                transfer_socket, transfer_port = setup_transfer_socket()
                response = create_response("ready", f"{filename} is ready for upload.", filename, transfer_port)
                start_transfer_thread(transfer_socket, filename, session, receive_file)

            # Unknown request type
            else:
                response = create_response("error", "Unknown request type.", "")

        # Send response to client
        conn.sendall(json.dumps(response).encode('utf-8'))

    except Exception as e:
        error_response = create_response("error", f"Failed to process request: {e}", "")
        conn.sendall(json.dumps(error_response).encode('utf-8'))
        print(f"[ERROR] Failed to process request: {e}")
