import socket
import threading
import time
import os
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

from server.decode import decode  # Assuming 'decode' is a function that processes incoming client data


class Server:
    """
    Server functionality includes:
        1. Accepting connections from clients
        2. Listening to clients' heartbeats
        3. Accepting requests for files from a client
        4. Accepting file uploads from a client
    """

    def __init__(self, broadcast_port=6000, timeout=100):
        self.FILE_TRANSFER_PORT = 6001
        self.BROADCAST_PORT = broadcast_port
        self.TIMEOUT = timeout
        self.CLIENTS = {}
        self.COUNT = 0
        self.running = True

    def broadcast_list(self):
        """Broadcast the list of active clients to all connected clients."""
        peer_list = [(client_id, addr) for client_id, (conn, addr) in self.CLIENTS.items()]
        peer_data = str(peer_list).encode('utf-8')

        for client_id, (conn, _) in self.CLIENTS.items():
            try:
                conn.sendall(peer_data)
                print(f"[BROADCAST] Client list {peer_list} broad casted to {client_id}.")
            except Exception as e:
                print(f"[ERROR] Could not send data to {client_id}: {e}")
                self.disconnect_client(client_id)

    def check_clients(self):
        """Check if clients are still connected by sending a heartbeat."""
        disconnected_clients = []
        for client_id, (conn, _) in self.CLIENTS.items():
            try:
                conn.send(b'')  # Send a small packet to check the connection
            except Exception as e:
                print(f"[DISCONNECT] {client_id} disconnected due to {e}.")
                disconnected_clients.append(client_id)

        for client_id in disconnected_clients:
            self.disconnect_client(client_id)

        if disconnected_clients:
            self.broadcast_list()

    def handle_client(self, conn, client_id):
        """Handle communication with a connected client."""
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    print(f"[INFO] No data received from {client_id}. Closing connection.")
                    break
                decode(data, conn, self.CLIENTS.values())
            except Exception as e:
                print(f"[ERROR] Error handling {client_id}: {e}. Checking active clients...")
                self.check_clients()
                break  # Exit loop if there's an error
        # Clean up on client disconnect
        self.disconnect_client(client_id)

    def disconnect_client(self, client_id):
        """Remove a client from the CLIENTS list and broadcast updated list."""
        if client_id in self.CLIENTS:
            conn, _ = self.CLIENTS[client_id]
            conn.close()
            del self.CLIENTS[client_id]
            print(f"[DISCONNECT] Client {client_id} has been removed.")
            self.broadcast_list()

    def timer(self):
        """Runs a timer that increments COUNT every second and checks for timed events."""
        start_time = time.time()
        while self.running:
            self.COUNT = int(time.time() - start_time)  # Update COUNT every second
            time.sleep(1)
            if self.COUNT % self.TIMEOUT == 0 and self.COUNT != 0:
                self.check_clients()

    def command_listener(self):
        """Listens for commands: 'q' to quit or 'c' to clear the screen."""
        while self.running:
            command = input().strip().lower()
            if command == 'q':
                self.running = False
                print(f"[SERVER] Shutting down after {self.COUNT} seconds.")
            elif command == 'c':
                os.system('cls' if os.name == 'nt' else 'clear')
                print("[SERVER] Screen cleared.")

    def start(self):
        """Start the server to listen for incoming connections and handle them."""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('0.0.0.0', self.BROADCAST_PORT))
        server_socket.listen()
        print("[SERVER] Listening for incoming connections...")

        # Start background threads for timer and command listener
        threading.Thread(target=self.timer, daemon=True).start()
        threading.Thread(target=self.command_listener, daemon=True).start()

        with ThreadPoolExecutor(max_workers=15) as executor:
            while self.running:
                try:
                    conn, addr = server_socket.accept()
                    client_id = conn.recv(1024).decode('utf-8').strip()

                    # If client ID is empty or not received correctly, generate a new one
                    if not client_id:
                        client_id = str(uuid4())
                        conn.sendall(client_id.encode('utf-8'))

                    # Store (conn, addr) tuple in CLIENTS dictionary
                    self.CLIENTS[client_id] = (conn, addr)
                    print(f"[CONNECT] New connection from {client_id} at {addr}")
                    executor.submit(self.handle_client, conn, client_id)

                except Exception as e:
                    print(f"[ERROR] {e}")

        # Clean up on shutdown
        server_socket.close()
        for client_id, (conn, _) in self.CLIENTS.items():
            conn.close()
        print("[SERVER] Server has shut down.")


if __name__ == '__main__':
    server = Server()
    server.start()
