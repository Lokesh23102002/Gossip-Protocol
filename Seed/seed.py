import socket
import threading
import sys
import time
from loggingseed import setup_logger
import argparse
import json
class Seed:
    def __init__(self, host, port, listen_thread):
        self.host = host
        self.port = port
        self.peers = {}
        self.running = True
        self.server_socket = None
        self.listen_thread = listen_thread

    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(self.listen_thread)
        self.server_socket.setblocking(False)
        logger.info(f"Server started on {self.host}:{self.port}")
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, address))
                client_thread.start()
            except BlockingIOError:
                time.sleep(0.1)
            except OSError:
                break

    def handle_client(self, client_socket, address):
        logger.info(f"Connection from {address}")
        recieved_message = client_socket.recv(1024).decode()
        message_json = json.loads(recieved_message)
        if recieved_message:
            if message_json["request Type"] == "ConnectSeed":
                self.peers[message_json["host"]+":"+str(message_json["port"])] = (message_json["host"], message_json["port"])
                logger.info(f"Added peer {address[0]}:{message_json['port']}")
                client_socket.close()

                peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                peer_socket.connect(self.peers[address[0]+":"+str(message_json["port"])])
                string_to_send = {"response Type": "ConnectedToSeed","host": self.host, "port": self.port}
                peer_socket.sendall(json.dumps(string_to_send).encode())
                peer_socket.close()
            elif message_json["request Type"] == "RequestPL":
                string_to_send = {"response Type": "PeerList", "peers": list(self.peers.keys())}
                client_socket.sendall(json.dumps(string_to_send).encode())
                client_socket.close()
            elif message_json["request Type"] == "Death":
                dead_peer = f"{message_json['host']}:{message_json['port']}"

                if dead_peer in self.peers:
                    self.peers.pop(dead_peer, None)
                    logger.info(f"Removed dead peer {dead_peer} as reported by {address[0]}")

                client_socket.close()




    def user_input(self):
        while self.running:
            try:
                user_input = input().strip().lower()
            except EOFError:
                self.running = False
                self.server_socket.close()
                print("Server stopped. Exiting...")
                sys.exit()
            
            if user_input == "exit":
                self.running = False
                self.server_socket.close()
                print("Server stopped. Exiting...")
                sys.exit()
            elif user_input == "peers":
                for peer in self.peers:
                    print(f"{peer}")
                    logger.info(f"Peer: {peer}")
          


def main():
    parser = argparse.ArgumentParser(description="P2P Seed")
    parser.add_argument("--port", type=int, default=1234, help="Port number for the seed to listen on")
    parser.add_argument("--max-peers", type=int, default=5, help="Maximum number of peers to connect to")
    parser.add_argument("--host", type=str, default="localhost", help="Host address of the seed")
    args = parser.parse_args()
    if args.host == "localhost":
        HOST = "localhost"
    elif args.host == "":
        HOST = socket.gethostbyname(socket.gethostname())
    else:
        HOST = args.host
    global logger 
    logger = setup_logger(f"logs/seed_{HOST}_{args.port}.log")
    logger.info(f"Starting seed on port {args.port}")
    logger.info(f"Maximum peers: {args.max_peers}")
    seed = Seed(HOST, args.port, args.max_peers)
    server_start_thread = threading.Thread(target=seed.start_server)
    server_start_thread.start()
    user_input_thread = threading.Thread(target=seed.user_input)
    user_input_thread.start()
    server_start_thread.join()
    user_input_thread.join()

if __name__ == '__main__':
    main()
