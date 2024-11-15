import sys
import threading
import time

from client.functions import connect, disconnect
from client.server_functions import receive_response, request_file, upload_file


class Client:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.notifications = []
        self.pause = threading.Event()
        self.stop = threading.Event()
        self.client_socket = connect(self.server_ip, self.server_port)

    def listen(self):
        while not self.stop.is_set():
            if self.pause.is_set():
                receive_response(self.client_socket, self.notifications)
            else:
                time.sleep(1)

    def show_notif(self):
        print("=======================[NOTIFICATIONS]======================]\n")
        if self.notifications:
            for notification in self.notifications:
                print(notification)
        else:
            print("no new notifications")

    def start(self):
        if not self.client_socket:
            print("[ERROR] Unable to connect to the server. Exiting...")
            sys.exit(1)

        notification_thread = threading.Thread(target=self.listen, daemon=True)
        notification_thread.start()

        try:
            while True:
                action = input("\n1. to request a file \n2. to upload a file "
                               "\n3. to view notifications \n4. to disconnect: \n").strip().lower()
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
                    self.show_notif()
                elif action == "4":
                    print("[DISCONNECT] Disconnecting from server...")
                    break
                else:
                    print("[ERROR] Invalid action")
        except Exception as e:
            print("[ERROR] {}".format(e))
        finally:
            self.stop.clear()
            notification_thread.join()
            disconnect(self.client_socket)
            print("[DISCONNECT] Disconnected from server...")


if __name__ == "__main__":
    client = Client("127.0.0.1", 6000)
    client.start()