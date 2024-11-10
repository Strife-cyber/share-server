def request_file(clients: [], filename: str) -> None:
    """
    Request a file from all active users
    :param clients: this is the list of connected clients' connections
    :param filename: this is the name of the file to request
    :return: None
    """
    request = json.dumps({"type": "request", "filename": filename})
    for client in clients:
        client.sendall(request.encode('utf-8'))  # Ensure the request is encoded before sending
    print(f"[REQUEST] file request for {filename} sent successfully")

def receive_file(conn, filename: str, buffer: int = 1024, save_path="uploads", session=None) -> None:
    """
    Receive a file from a connected client
    :param conn: the connected client socket
    :param filename: the name of the file being received
    :param buffer: the buffer size to receive the file
    :param save_path: the path to save the received file
    :param session: the database session to use for file management
    :return: None
    """
    if session is None:
        raise ValueError("Session cannot be None")

    try:
        os.makedirs(save_path, exist_ok=True)

        if not filename:
            print("[ERROR] filename cannot be empty")
            return

        file_path = os.path.join(save_path, filename)

        with open(file_path, "wb") as file:
            print(f"[RECEIVING FILE] {filename}")
            while True:
                data = conn.recv(buffer)
                if not data:
                    break  # Exit if no more data is received
                file.write(data)

        print(f"[RECEIVING FILE] {filename} received successfully")

        retrieve_file = Files.get_by_name(session, filename)
        if retrieve_file:
            Files.update_uploaded_status(session, retrieve_file.id, True)
        else:
            Files.create(session, filename, True)

    except Exception as e:
        print(f"[ERROR] file reception error: {e}")


import json
import os
import socket

from database.connect import Files


def send_file(conn: socket.socket, filename: str, buffer: int = 1024, session=None) -> None:
    """
    Sends a file to a connected client on a dedicated connection.
    :param conn: this is the temporary socket connection for file transfer
    :param filename: this is the name of the file to send
    :param buffer: this is the buffer size to send the file
    :param session: the database session to use for file management
    :return: None
    """
    if session is None:
        raise ValueError("Session cannot be None")

    try:
        # Confirm file exists in database
        file_record = Files.get_by_name(session, filename)
        if not file_record:
            print("[ERROR] file not found in database")
            return

        # Define file path
        file_path = os.path.join("uploads", filename)
        if not os.path.exists(file_path):
            print(f"[ERROR] file {filename} does not exist in storage")
            return

        # Open and send file data
        with open(file_path, "rb") as file:
            print(f"[SENDING FILE] Starting to send {filename}")
            while True:
                data = file.read(buffer)
                if not data:
                    break  # Stop when the file is completely read
                conn.sendall(data)

        print(f"[SENDING FILE] {filename} sent successfully")

    except FileNotFoundError:
        print("[ERROR] file not found on server")
    except Exception as e:
        print(f"[ERROR] file sending error: {e}")
    finally:
        conn.close()  # Close the dedicated file transfer connection
        print("[CONNECTION CLOSED] File transfer connection closed")

