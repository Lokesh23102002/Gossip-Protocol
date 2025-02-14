import os
import sys
import argparse
import socket
import threading
from loggingpeer import setup_logger
import csv
import asyncio
import random
import time
import json


class Peer:
    def __init__(self, host, port,listen_thread):
        self.host = host
        self.port = port
        self.peers = {}
        self.seeds = {}
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
            
    def connect_to_seeds(self):
        seed_list = {}
        with open('Peer/config.csv', 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                self.seeds[row[0]+":"+row[1]] = {'host': row[0], 'port': int(row[1])}
        selected_seed = random.sample(list(self.seeds.keys()), len(self.seeds)//2 + 1)
        # print(self.seeds)
        # print(selected_seed)

        for seed in selected_seed:
            seed_thread = threading.Thread(target=self.connect_to_seed, args=((self.seeds[seed]['host'],self.seeds[seed]['port']),))
            seed_thread.start()
            seed_thread.join()
    
    def connect_to_seed(self, seed):
        logger.info(f"Connecting to seed {seed}")
        seed_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        seed_socket.connect(seed)
        self.seeds[seed[0]+":"+str(seed[1])]['connection'] = False
        message = {"request Type": "Connect","host": self.host, "port": self.port}
        while not self.seeds[seed[0]+":"+str(seed[1])]['connection']:
            seed_socket.sendall(json.dumps(message).encode())
            time.sleep(0.1)

        seed_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        seed_socket.connect(seed)
        string_to_send = {"request Type": "RequestPL"}
        seed_socket.sendall(json.dumps(string_to_send).encode())
        recieved_message = seed_socket.recv(1024).decode()
        message = json.loads(recieved_message)
        logger.info(f"Recieved peer {message}")
        if message["response Type"] == "PeerList":
            for peer in message["peers"]:
                if(peer != self.host+":"+str(self.port)):
                    self.peers[peer]= {"connection":False,"Recieved_from":seed}
        seed_socket.close()

    def handle_client(self, client_socket, address):
        logger.info(f"Connection from {address}")
        recieved_message = client_socket.recv(1024).decode()
        if recieved_message:
            message = json.loads(recieved_message)
            if message["response Type"] == "ConnectedToSeed":
                self.seeds[message["host"]+":"+str(message["port"])]['connection'] = True
                logger.info(f"Received message: {recieved_message}")
                client_socket.close()
            else:
                client_socket.close()

    def user_input(self):
        while True:
            try:
                user_input = input()
                if user_input == 'q':
                    self.running = False  # Stop the server
                    try:
                        self.server_socket.close()
                    except OSError:
                        pass
                    print("Server stopped. Exiting...")
                    sys.exit()
                elif user_input == 'p':
                    print("Connected peers:")
                    for peer in self.peers:
                        print(f"{peer}:{self.peers[peer]}")
                elif user_input == 's':
                    print("Connected seeds:")
                    for seed in self.seeds:
                        print(f"{seed}:{self.seeds[seed]}")
            except EOFError:
                self.running = False 
                print("Input stream closed unexpectedly. Exiting...")
                sys.exit()



def __main__():
    parser = argparse.ArgumentParser(description="P2P Peer")
    parser.add_argument("--port", type=int, default=3000,help="Port number for the peer to listen on")
    parser.add_argument("--max-peers", type=int,default = 5, help="Maximum number of peers to connect to")
    args = parser.parse_args()
    HOST = socket.gethostbyname(socket.gethostname())
    # HOST = '127.0.0.1'
    global logger
    logger = setup_logger(f"logs/peer_{HOST}_{args.port}.log")
    logger.info(f"Starting peer on port {args.port}")
    logger.info(f"Maximum peers: {args.max_peers}")
    logger.info(f"Host IP: {HOST}")
    peer = Peer(HOST, args.port, args.max_peers)
    logger.info("Starting server...")
    # Start the server in a separate thread
    server_thread = threading.Thread(target=peer.start_server, daemon=True)
    server_thread.start()

    # Start seed connection in another thread
    seed_thread = threading.Thread(target=peer.connect_to_seeds, daemon=True)
    seed_thread.start()
    
    # Start user input thread
    user_input_thread = threading.Thread(target=peer.user_input, daemon=True)
    user_input_thread.start()
    # Join both threads to keep the program running
    server_thread.join()
    seed_thread.join()
    user_input_thread.join()

if __name__ == '__main__':
    __main__()
        


