import os
import json
import socket
from datetime import datetime

def send_request(client_socket: socket.socket, request: dict) -> dict:
    """
    Sends a JSON request to the server and receives the JSON response.
    :param client_socket: The socket connected to the server
    :param request: The JSON request to send
    :return: Decoded JSON response from the server
    """
    client_socket.sendall(json.dumps(request).encode('utf-8'))
    response_data = client_socket.recv(1024).decode('utf-8')
    return json.loads(response_data)

def request_file(client_socket: socket.socket, filename: str) -> None:
    """
    Requests a file from the server.
    :param client_socket: The socket connected to the server
    :param filename: The name of the file to request
    :return: None
    """
    try:
        response = send_request(client_socket, {"type": "request", "filename": filename})
        response_status = response.get("status")

        if response_status == "pending":
            print(f"[INFO] {response.get('message')}")
        elif response_status == "ready":
            transfer_port = response.get("transfer_port")
            print(f"[INFO] {response.get('message')} on port {transfer_port}")
            file_path = os.path.join('downloads', filename)

            # Connect to the provided transfer port to receive file data
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as transfer_socket:
                transfer_socket.connect(('127.0.0.1', transfer_port))

                with open(file_path, 'wb') as file:
                    while True:
                        data = transfer_socket.recv(1024)
                        if not data:
                            break
                        file.write(data)
            print(f"[RECEIVED] File '{filename}' received successfully.")

        elif response_status == "error":
            print(f"[ERROR] {response.get('message')}")
        else:
            print("[ERROR] Unexpected response from server", response)

    except Exception as e:
        print(f"[ERROR] Failed to request file '{filename}': {e}")


def upload_file(client_socket: socket.socket, filename: str, filepath: str, buffer_size: int = 1024) -> None:
    """
    Uploads a file to the server.
    :param client_socket: The socket connected to the server
    :param filename: The name of the file to upload
    :param filepath: The path to the file to upload
    :param buffer_size: Buffer size for reading file data
    :return: None
    """
    try:
        response = send_request(client_socket, {"type": "upload", "filename": filename})
        transfer_port = response.get("transfer_port")
        print(f"[INFO] {response.get('message')} on port {transfer_port}")

        # Connect to the provided transfer port to send file data
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as transfer_socket:
            transfer_socket.connect(('127.0.0.1', transfer_port))

            with open(filepath, 'rb') as file:
                while data := file.read(buffer_size):
                    transfer_socket.sendall(data)

        print(f"[UPLOAD] File '{filename}' uploaded successfully.")

    except Exception as e:
        print(f"[ERROR] Failed to upload file '{filename}': {e}")


def receive_response(client_socket: socket.socket, notifications: list, peer_list: dict) -> None:
    """
    Receives server notifications and appends them to a list.
    :param client_socket: The socket connected to the server
    :param notifications: The list of notifications
    :param peer_list: The peer list (modified in place if updated)
    :return: None
    """
    try:
        # Receive data from the server
        response_data = client_socket.recv(1024).decode('utf-8')

        try:
            # Try to parse the response data as JSON
            response = json.loads(response_data)

            # Append the message to the notifications
            notifications.append({
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"): response.get('message')
            })

            # If the response is of type "list", update the peer list
            if response.get("type") == "list":
                # Update the peer list in place with the received list
                peer_list.update({client_id: port for client_id, port in response.get("message", [])})

        except json.JSONDecodeError:
            # If the data is not JSON, treat it as a raw message
            notifications.append({
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"): f"Updated client list: {response_data}"
            })

    except Exception as e:
        print(f"[ERROR] Failed to receive response from server: {e}")
