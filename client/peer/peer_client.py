import socket
import threading
import json
from datetime import datetime
from client.peer.peer_functions import send_message

# Constants
BUFFER_SIZE = 1024

class PeerClient:
    def __init__(self, port=None):
        self.messages = []
        self.notifications = []
        self.connections = {}  # Dictionary to store peer sockets {peer_id: socket}
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.bind(("localhost", port or 0))  # Bind to the given port or let the OS pick
        self.port = self.client_socket.getsockname()[1]  # Retrieve the actual port bound
        self.client_socket.listen()  # Allow incoming connections
        print(f"[PEER] Peer client connected on port {self.port}")

    def accept_connections(self):
        """Accept incoming peer connections."""
        while True:
            conn, addr = self.client_socket.accept()
            print(f"[CLIENT {self.port}] Incoming connection from {addr}")
            threading.Thread(target=self.handle_peer, args=(conn,), daemon=True).start()

    def handle_peer(self, conn):
        """Handle communication with a single peer."""
        try:
            while True:
                data = conn.recv(BUFFER_SIZE).decode('utf-8')
                if not data:
                    break
                message = json.loads(data)
                self.messages.append(message)
                self.notifications.append({
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"): f"[MESSAGE] {message['id']}: {message['message']}"
                })
                print(f"[RECEIVED from {message['id']}] {message['message']}")
        except Exception as e:
            print(f"[ERROR] Connection error: {e}")
        finally:
            conn.close()

    def connect_to_peer(self, peer_id, peer_port):
        """Connect to a peer."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(("localhost", peer_port))
            self.connections[peer_id] = sock
            print(f"[CLIENT {self.port}] Connected to peer {peer_id} on port {peer_port}")
            threading.Thread(target=self.handle_peer, args=(sock,), daemon=True).start()
        except Exception as e:
            print(f"[ERROR] Could not connect to peer {peer_id} on port {peer_port}: {e}")

    def show_messages(self):
        """Display all received messages."""
        print("[MESSAGES]")
        for msg in self.messages:
            print(f"{msg['id']}: {msg['message']}")

    def show_notifications(self):
        """Display all notifications."""
        print("[NOTIFICATIONS]")
        for notif in self.notifications:
            for timestamp, message in notif.items():
                print(f"{timestamp}: {message}")

    def send_message_to_peer(self, peer_id, message):
        """Send a message to a peer."""
        if peer_id not in self.connections:
            print(f"[ERROR] Peer {peer_id} is not connected.")
            return
        send_message(self.connections[peer_id], message, f"Client-{self.port}", self.messages)

    def start(self):
        """Start the client and the command loop."""
        # Start listening for incoming connections in a separate thread
        threading.Thread(target=self.accept_connections, daemon=True).start()

if __name__ == "__main__":
    # Start a single client with a custom port or auto-assign a port
    client_port = int(input("Enter your client port (or press Enter to auto-assign): ").strip() or 0)
    client = PeerClient(client_port)
    client.start()
