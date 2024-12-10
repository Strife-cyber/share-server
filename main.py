from client.clients import Client
from server.servers import Server

def main():
    """
    The main function to run. Let us hope it works
    :return: None
    """
    run = input().strip().lower()
    if run == "client":
        ip = input('Enter IP Address: ').strip()
        if ip:
            client = Client(ip, 6000)
            client.start()
        else:
            client = Client("127.0.0.1", 6000)
            client.start()
    elif run == "server":
        ip = input('Enter IP Address: ').strip()
        if ip:
            server = Server(address=ip)
            server.start()
        else:
            server = Server('0.0.0.0')
            server.start()
if __name__ == "__main__":
    main()