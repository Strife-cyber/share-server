import socket
import threading
import json
from datetime import datetime
from peer_functions import send_message

# Constants
BUFFER_SIZE = 1024

# Utility Functions (Assumed Available)
# check_presence, send_message, listen

def start_client(port):
    messages = []
    notifications = []
    connections = {}  # Dictionary to store peer sockets {peer_id: socket}

    # Socket for this client to listen for incoming connections
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.bind(("localhost", port))
    client_socket.listen(10)  # Allow up to 10 connections
    print(f"[CLIENT {port}] Listening on port {port}...")

    def accept_connections():
        while True:
            conn, addr = client_socket.accept()
            print(f"[CLIENT {port}] Incoming connection from {addr}")
            threading.Thread(target=handle_peer, args=(conn,), daemon=True).start()

    def handle_peer(conn):
        """Handle communication with a single peer."""
        try:
            while True:
                data = conn.recv(BUFFER_SIZE).decode('utf-8')
                if not data:
                    break
                message = json.loads(data)
                messages.append(message)
                notifications.append({
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"): f"[MESSAGE] {message['id']}: {message['message']}"
                })
                print(f"[RECEIVED from {message['id']}] {message['message']}")
        except Exception as e:
            print(f"[ERROR] Connection error: {e}")
        finally:
            conn.close()

    def connect_to_peer(peer_id, peer_port):
        """Connect to a peer."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(("localhost", peer_port))
            connections[peer_id] = sock
            print(f"[CLIENT {port}] Connected to peer {peer_id} on port {peer_port}")
            threading.Thread(target=handle_peer, args=(sock,), daemon=True).start()
        except Exception as e:
            print(f"[ERROR] Could not connect to peer {peer_id} on port {peer_port}: {e}")

    # Start listening for incoming connections
    threading.Thread(target=accept_connections, daemon=True).start()

    # Command loop
    while True:
        print("\n[OPTIONS]")
        print("1. Connect to a new peer")
        print("2. Send a message")
        print("3. Show messages")
        print("4. Show notifications")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            # Connect to a new peer
            peer_id = input("Enter peer ID: ").strip()
            peer_port = int(input("Enter peer port: ").strip())
            connect_to_peer(peer_id, peer_port)
        elif choice == "2":
            # Send a message to a peer
            if not connections:
                print("[ERROR] No connected peers. Connect to a peer first.")
                continue
            print(f"Connected peers: {list(connections.keys())}")
            peer_id = input("Enter peer ID to message: ").strip()
            if peer_id not in connections:
                print("[ERROR] Peer not connected.")
                continue
            message = input("Enter your message: ").strip()
            send_message(connections[peer_id], message, f"Client-{port}", messages)
        elif choice == "3":
            # Show all messages
            print("[MESSAGES]")
            for msg in messages:
                print(f"{msg['id']}: {msg['message']}")
        elif choice == "4":
            # Show all notifications
            print("[NOTIFICATIONS]")
            for notif in notifications:
                for timestamp, message in notif.items():
                    print(f"{timestamp}: {message}")
        else:
            print("[ERROR] Invalid choice. Try again.")


if __name__ == "__main__":
    # Start a single client
    client_port = int(input("Enter your client port: ").strip())
    start_client(client_port)
