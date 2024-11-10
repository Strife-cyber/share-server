from client.clients import Client
from server.servers import Server

def main():
    """
    The main function to run. Let us hope it works
    :return: None
    """
    run = input().strip().lower()
    if run == "client":
        client = Client("127.0.0.1", 6000)
        client.start()
    elif run == "server":
        server = Server()
        server.start()

if __name__ == "__main__":
    main()