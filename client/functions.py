import uuid
import socket

from client.data_function import read_json, verify_hash, hash_string, append_json


def status(email: str, password: str) -> (bool, str):
    clients: list = read_json()
    for client in clients:
        if client['email'] == email and verify_hash(password, client['password']):
            return True, client['id']
    return False, None


def register(email: str, password: str) -> (bool, str):
    try:
        new_id: str = str(uuid.uuid4())
        new_client = {"email": email, "password": hash_string(password), "id": new_id}
        append_json(new_client)
        return True, new_id
    except Exception as e:
        print(f"An exception occurred: {e}")
        return False, None


def prerequisite():
    email = input("Enter your email: ")
    password = input("Enter your password: ")

    stat, user_id = status(email, password)
    if not stat:
        stat, user_id = register(email, password)

    return user_id


def connect(ip: str, port: int) -> socket:
    """
    Establishes a connection to the server using TCP
    :param ip: the ip address of the server
    :param port: the port of the server
    :return: returns the client socket
    """
    client_id = prerequisite()
    client_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((ip, port))
        client_socket.sendall(str(client_id).encode('utf-8'))
        print(f"[CONNECTION] connected to server at {ip}:{port}")
        return client_socket
    except Exception as e:
        print(f"[ERROR] An exception occurred: {e}")
        client_socket.close()
        return None


def disconnect(client_socket: socket) -> None:
    try:
        client_socket.sendall(b"DISCONNECT")
    except:
        pass  # Ignore any errors during disconnection
    finally:
        client_socket.close()
        print(f"[DISCONNECT] Disconnected from server")
