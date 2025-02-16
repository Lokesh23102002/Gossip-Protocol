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

class MessageList:

    def __init__(self):
        self.messageList = {} # Initialize ML

    def insert(self, msg, IP): # Check if present, if not then add
        message = msg
        messageHash = hash(msg)
        senderIP = IP

        if messageHash in self.messageList.keys():
            return False
        else:
            self.messageList[messageHash] = f"{message}:{senderIP}:{messageHash}"
            return True
    
    def check(self, msg): # Check if present, return true, else return False
        messageHash = hash(msg)
        if messageHash in self.messageList.keys():
            return True
        else:
            return False   

class Peer:
    def __init__(self, host, port,listen_thread):
        self.host = host
        self.port = port
        self.peers = {}
        self.seeds = {}
        self.running = True
        self.server_socket = None
        self.listen_thread = listen_thread
        self.messageList = MessageList()
        self.lock = threading.Lock()

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
        logger.debug(f"Connecting to seed {seed}")

        try:
            seed_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            seed_socket.settimeout(3)  # Prevent blocking
            seed_socket.connect(seed)

            seed_key = f"{seed[0]}:{seed[1]}"
            self.seeds[seed_key]['connection'] = False

            message = {"request Type": "ConnectSeed", "host": self.host, "port": self.port}

            for _ in range(10):  # Retry up to 10 times, then give up
                try:
                    seed_socket.sendall(json.dumps(message).encode())
                    time.sleep(0.1)

                    if self.seeds[seed_key]['connection']:
                        break  # Stop sending once connected
                except (BrokenPipeError, ConnectionResetError) as e:
                    logger.debug(f"Failed to send data to seed {seed}: {e}")
                    return  # Stop execution on failure

            # Close the first socket before creating a new one
            seed_socket.close()

            # New socket to request Peer List (PL)
            seed_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            seed_socket.settimeout(3)  
            seed_socket.connect(seed)

            request_pl = {"request Type": "RequestPL"}
            seed_socket.sendall(json.dumps(request_pl).encode())

            received_message = seed_socket.recv(1024).decode()
            message = json.loads(received_message)

            logger.info(f"Received peer list from {seed}: {message}")

            if message.get("response Type") == "PeerList":
                for peer in message.get("peers", []):
                    if peer != f"{self.host}:{self.port}":
                        self.peers[peer] = {"connection": False, "Received_from": seed}

            seed_socket.close()

            self.connect_to_peers()

        except (socket.timeout, ConnectionRefusedError) as e:
            logger.error(f"Failed to connect to seed {seed}: {e}")

        finally:
            if seed_socket:
                seed_socket.close()  # Ensure socket is closed

    
    def connect_to_peers(self):
        logger.debug("Starting peer connections...")

        for peer in self.peers.keys():
            if self.peers[peer]["connection"]:  # Skip already connected peers
                logger.debug(f"Skipping already connected peer: {peer}")
                continue

            peer_host, peer_port = peer.split(":")
            peer_port = int(peer_port)

            peer_thread = threading.Thread(target=self.connect_to_peer, args=(peer_host, peer_port))
            peer_thread.start()
    
    def connect_to_peer(self, peer_host, peer_port):
        logger.debug(f"Attempting connection to peer {peer_host}:{peer_port}")

        try:
            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_socket.settimeout(2)  # Set timeout
            peer_socket.connect((peer_host, peer_port))

            # Send connection request
            message = {"request Type": "ConnectPeer", "host": self.host, "port": self.port}
            peer_socket.sendall(json.dumps(message).encode())

            # Wait for response
            response = peer_socket.recv(1024).decode()
            if response:
                response_data = json.loads(response)
                if response_data.get("response Type") == "ConnectedToPeer":
                    self.peers[f"{peer_host}:{peer_port}"]["connection"] = True
                    logger.info(f"Successfully connected to peer {peer_host}:{peer_port}")
                else:
                    logger.warning(f"Unexpected response from {peer_host}:{peer_port}: {response_data}")

            peer_socket.close()

        except (socket.timeout, ConnectionRefusedError) as e:
            logger.error(f"Failed to connect to peer {peer_host}:{peer_port}: {e}")
        
        finally:
            if peer_socket:
                peer_socket.close()


    def handle_client(self, client_socket, address):
        logger.debug(f"Connection from {address}")
        
        try:
            received_message = client_socket.recv(1024).decode()
            if not received_message:
                return  # No data received, ignore the request

            message = json.loads(received_message)

            if message.get("response Type") == "ConnectedToSeed":
                # Handling seed connection acknowledgment
                seed_key = f"{message['host']}:{message['port']}"
                self.seeds[seed_key]['connection'] = True
                logger.debug(f"Received seed connection confirmation: {received_message}")

            elif message.get("request Type") == "ConnectPeer":
                # Handling peer connection request
                peer_key = f"{message['host']}:{message['port']}"

                # If peer is not already connected, add it to the peer list
                if peer_key not in self.peers:
                    self.peers[peer_key] = {"connection": True, "Received_from": address}
                    logger.debug(f"New peer added: {peer_key}")

                # Send confirmation response
                response = {"response Type": "ConnectedToPeer"}
                client_socket.sendall(json.dumps(response).encode())
                logger.debug(f"Sent connection confirmation to {peer_key}")

            elif message.get("request Type") == "Gossip":
                gossip_msg = message["message"]
                
                if not self.messageList.check(gossip_msg):  # Avoid duplicate propagation
                    logger.info(f"Received gossip message: {gossip_msg}")

                    # Store the message to prevent reprocessing
                    self.messageList.insert(gossip_msg, address[0])

                    # Forward the message to other peers
                    for peer in self.peers.keys():
                        if peer != f"{message['host']}:{message['port']}" and self.peers[peer]["connection"]:
                            peer_host, peer_port = peer.split(":")
                            peer_port = int(peer_port)
                            self.send_message_to_peer(peer_host, peer_port, gossip_msg)


        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received from {address}")

        except Exception as e:
            logger.error(f"Error handling client {address}: {e}")

        finally:
            client_socket.close()  # Ensure socket closure


    def gossip_message(self):
        """Generate and send gossip messages every 5 seconds to all connected peers."""
        message_count = 0

        while message_count < 10:  # Generate only 10 messages
            timestamp = int(time.time())
            message = f"{timestamp}:{self.host}:{self.port}:{message_count}"

            if self.messageList.insert(message, self.host):  # Prevent duplicate propagation
                logger.debug(f"Generated gossip message: {message}")

                # Lock peers list while iterating to avoid race conditions
                with self.lock:
                    for peer in list(self.peers.keys()):  # Convert to list to avoid runtime modification errors
                        if self.peers[peer]["connection"]:
                            peer_host, peer_port = peer.split(":")
                            peer_port = int(peer_port)
                            self.send_message_to_peer(peer_host, peer_port, message)

            message_count += 1
            time.sleep(5)  # Wait 5 seconds before sending the next message


    def send_message_to_peer(self, peer_host, peer_port, message):
        """Send a gossip message to a connected peer."""
        try:
            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_socket.settimeout(2)  # Set timeout
            peer_socket.connect((peer_host, peer_port))

            # Wrap the message in JSON format
            message_data = {"request Type": "Gossip", "message": message,"host": self.host, "port": self.port}
            peer_socket.sendall(json.dumps(message_data).encode())

            logger.debug(f"Sent gossip message to {peer_host}:{peer_port}")
            peer_socket.close()
        
        except (socket.timeout, ConnectionRefusedError) as e:
            logger.error(f"Failed to send gossip message to {peer_host}:{peer_port}: {e}")
    
    def check_peer_liveness(self):
        """Checks if connected peers are alive by attempting to open a TCP connection."""
        logger.debug("Starting peer liveliness check thread...")  # Debugging log

        while self.running:
            logger.debug("Liveliness thread is active.")  # Debugging log

            with self.lock:
                for peer in list(self.peers.keys()):
                    if not self.peers[peer].get("connection", False):
                        logger.debug(f"Skipping inactive peer: {peer}")
                        continue

                    peer_host, peer_port = peer.split(":")
                    peer_port = int(peer_port)
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)

                    try:
                        sock.connect((peer_host, peer_port))
                        sock.close()
                        self.peers[peer]["ping_failures"] = 0  # Reset failure count
                        logger.debug(f"Peer {peer} is alive.")

                    except (socket.timeout, ConnectionRefusedError):
                        self.peers[peer]["ping_failures"] = self.peers.get(peer, {}).get("ping_failures", 0) + 1
                        logger.warning(f"Peer {peer} is unresponsive ({self.peers[peer]['ping_failures']} failures).")

                        if self.peers[peer]["ping_failures"] >= 3:
                            logger.error(f"Peer {peer} is dead! Removing and notifying seeds.")
                            self.peers.pop(peer, None)
                            for seed, seed_info in self.seeds.items():
                                if seed_info.get("connection", False):  # Notify only if the seed is connected
                                    self.notify_seed_of_death(seed, peer_host, peer_port)


                    finally:
                        sock.close()

            time.sleep(13)  # Delay before the next check



    def notify_seed_of_death(self, seed, dead_host, dead_port):
        """Notifies a seed node that a peer is no longer alive."""
        try:
            seed_host, seed_port = seed.split(":")
            seed_port = int(seed_port)

            seed_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            seed_socket.settimeout(2)
            seed_socket.connect((seed_host, seed_port))

            message = {"request Type": "Death", "host": dead_host, "port": dead_port}
            seed_socket.sendall(json.dumps(message).encode())

            logger.debug(f"Notified seed {seed} about dead peer {dead_host}:{dead_port}")
            seed_socket.close()

        except (socket.timeout, ConnectionRefusedError) as e:
            logger.error(f"Failed to notify seed {seed} about dead peer: {e}")





    def user_input(self):
        while True:
            try:
                user_input = input().strip().lower()  # Convert to lowercase and remove leading/trailing spaces

                if user_input == 'exit':
                    self.running = False  # Stop the server
                    try:
                        self.server_socket.close()
                    except OSError:
                        pass
                    print("Server stopped. Exiting...")
                    sys.exit()

                elif user_input == 'peers':
                    print("Connected peers:")
                    for peer in self.peers:
                        print(f"{peer}: {self.peers[peer]}")

                elif user_input == 'seeds':
                    print("Connected seeds:")
                    for seed in self.seeds:
                        print(f"{seed}: {self.seeds[seed]}")

                elif user_input == 'msg':
                    print("Received Messages:")
                    if not self.messageList.messageList:
                        print("No messages received yet.")
                    else:
                        for msg_hash, msg_data in self.messageList.messageList.items():
                            print(f"{msg_data}")

            except EOFError:
                self.running = False
                print("Input stream closed unexpectedly. Exiting...")
                sys.exit()




def __main__():
    parser = argparse.ArgumentParser(description="P2P Peer")
    parser.add_argument("--port", type=int, default=3000,help="Port number for the peer to listen on")
    parser.add_argument("--max-peers", type=int,default = 5, help="Maximum number of peers to connect to")
    parser.add_argument("--host", type=str, default="localhost", help="Host IP address")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()
    if args.host == "localhost":
        HOST = "localhost"
    elif args.host == "":
        HOST = socket.gethostbyname(socket.gethostname())
    # HOST = '127.0.0.1'
    global logger
    if(args.debug):
        logger = setup_logger(f"logs/peer_{HOST}_{args.port}.log", debug=True)
    else:
        logger = setup_logger(f"logs/peer_{HOST}_{args.port}.log")
    logger.info(f"Starting peer on port {args.port}")
    logger.info(f"Maximum peers: {args.max_peers}")
    logger.info(f"Host IP: {HOST}")
    peer = Peer(HOST, args.port, args.max_peers)
    logger.info("Starting server...")

    # 1. Start server thread (runs indefinitely)
    server_thread = threading.Thread(target=peer.start_server, daemon=True)
    server_thread.start()

    # 2. Start user input thread (runs indefinitely)
    user_input_thread = threading.Thread(target=peer.user_input, daemon=True)
    user_input_thread.start()

    # 3. Start seed connection thread
    seed_thread = threading.Thread(target=peer.connect_to_seeds, daemon=True)
    seed_thread.start()
    seed_thread.join()  # Wait for seed connections to complete before proceeding

    # 4. Start peer liveness check thread (after seed connection)
    liveness_thread = threading.Thread(target=peer.check_peer_liveness, daemon=True)
    liveness_thread.start()

    # 5. Start gossip message thread (last)
    gossip_thread = threading.Thread(target=peer.gossip_message, daemon=True)
    gossip_thread.start()

    # Ensure that necessary threads keep running
    server_thread.join()
    user_input_thread.join()
    

if __name__ == '__main__':
    __main__()
        


