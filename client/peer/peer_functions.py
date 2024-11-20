"""
This function are here to generally handle p2p connections for clients currently
on the network may be a bit rough but will work out
"""
import json
import socket

from datetime import datetime

"""
In our previous study we had some interesting functions but we will not use some of them
"""

def check_presence(conn: socket.socket) -> bool:
    """
    This function checks if the client is present on the network and has not yet been
    disconnected.
    :param conn: socket object of the client
    :return: None
    """
    try:
        conn.send(b'')  # Send a small packet to check the connection
        return True
    except Exception as e:
        print(f"[DISCONNECT] The client you just tried to connect to was not found \n This is due to {e}")
        return False


def send_message(conn: socket.socket, message: str, sender_id: str, messages: []) -> None:
    """
    This function sends a message to the client
    :param conn: socket object of the client
    :param message: message to be sent
    :param sender_id: id of the sender
    :param messages: messages received and sent
    :return: None
    """
    if check_presence(conn):
        try:
            conn.sendall(json.dumps({'id': sender_id, 'message': message}).encode('utf-8'))
            messages.append({'id': sender_id, 'message': message})
        except Exception as e:
            print(f"[ERROR] Something went wrong {e}")


def listen(peer_socket: socket.socket, messages: [], notifications: []) -> None:
    """
    This function listens for messages from other clients
    :param peer_socket: socket object of the client
    :param messages: list of messages received from other clients and sent
    :param notifications: list of notifications
    :return: None
    """
    try:
        message = peer_socket.recv(1024).decode('utf-8')
        messages.append(json.loads(message))
        notifications.append({datetime.now().strftime("%Y-%m-%d %H:%M:%S"): f"[MESSAGE] New message received"})
    except Exception as error:
        print(f"[ERROR] Listening error: {error}")
        