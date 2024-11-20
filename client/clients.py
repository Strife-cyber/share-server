import sys
import time
import threading

from client.functions import connect
from client.peer.peer_client import PeerClient
from client.server_functions import receive_response, request_file, upload_file


class Client:
    """Handles the basic client functionalities."""

    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.notifications = []
        self.pause = threading.Event()
        self.stop = threading.Event()
        self.peer_client = PeerClient()
        self.peer_list = {}
        self.client_socket = connect(self.server_ip, self.server_port, self.peer_client.port)

    def listen_for_server_messages(self):
        """Listen for messages from the server."""
        while not self.stop.is_set():
            try:
                if self.pause.is_set():
                    receive_response(self.client_socket, self.notifications, self.peer_list)
                else:
                    time.sleep(1)
            except Exception as e:
                print(f"[ERROR] Listening error: {e}")
                self.stop.set()

    def show_notifications(self):
        """Display notifications."""
        print("=======================[NOTIFICATIONS]======================\n")
        if self.notifications:
            for notification in self.notifications:
                print(notification)
        else:
            print("No new notifications")

    def start(self):
        """Start the client and handle menu options."""
        if not self.client_socket:
            print("[ERROR] Unable to connect to the server. Exiting...")
            sys.exit(1)

        # Start server message listener
        self.pause.set()
        threading.Thread(target=self.listen_for_server_messages, daemon=True).start()
        self.peer_client.start()

        try:
            while True:
                action = input("\n1. Request a file\n2. Upload a file\n3. View notifications\n4. Disconnect\n5. Connect to a new peer\n6. Send a message\n7. Show messages\n").strip()
                if action == "1":
                    filename = input("Enter file name to request: ").strip()
                    self.pause.clear()
                    request_file(self.client_socket, filename)
                    self.pause.set()
                elif action == "2":
                    filename = input("Enter file name to upload: ").strip()
                    filepath = input("Enter file path: ").strip()
                    self.pause.clear()
                    upload_file(self.client_socket, filename, filepath)
                    self.pause.set()
                elif action == "3":
                    self.show_notifications()
                elif action == "4":
                    print("[DISCONNECT] Disconnecting from server...")
                    break
                elif action == "5":
                    # Connect to a new peer
                    peer_id = input("Enter peer ID: ").strip()
                    if self.peer_list[peer_id]:
                        self.peer_client.connect_to_peer(peer_id, self.peer_list[peer_id])
                    else:
                        print("[ERROR] Peer ID not found")
                elif action == "6":
                    # Send a message to a peer
                    if not self.peer_client.connections:
                        print("[ERROR] No connected peers. Connect to a peer first.")
                        continue
                    print(f"Connected peers: {list(self.peer_client.connections.keys())}")
                    peer_id = input("Enter peer ID to message: ").strip()
                    message = input("Enter your message: ").strip()
                    self.peer_client.send_message_to_peer(peer_id, message)
                elif action == "7":
                    self.peer_client.show_messages()
                else:
                    print("[ERROR] Invalid action")
        except Exception as e:
            print(f"[ERROR] {e}")
        finally:
            self.stop.set()  # Set stop event for the listener thread
            self.client_socket.close()
            print("[DISCONNECT] Disconnected from server...")


if __name__ == "__main__":
    client = Client("127.0.0.1", 6000)
    client.start()
