import uuid
import socket

from client.data_function import read_json, verify_hash, hash_string, append_json


def status(email: str, password: str) -> (bool, str):
    """
    This function reads the data json file and checks for the user then returns
    his id if he exists
    :param email: this is the email of the user
    :param password: this is the password of the user
    :return: returns a tuple of bool and str
    """
    clients: list = read_json()
    for client in clients:
        if client['email'] == email and verify_hash(password, client['password']):
            return True, client['id']
    return False, None


def register(email: str, password: str) -> (bool, str):
    """
    This function registers a new user
    :param email: the user's email
    :param password: the user's password
    :return: a tuple of bool and a string which is the id
    """
    try:
        new_id: str = str(uuid.uuid4())
        new_client = {"email": email, "password": hash_string(password), "id": new_id}
        append_json(new_client)

        return True, new_id
    except Exception as e:
        print("An exception occurred: {}".format(e))
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
    """
    Closes the connection to the server
    :param client_socket: this is the client socket
    :return: None
    """
    client_socket.close()
    print(f"[DISCONNECT] disconnected from server")
