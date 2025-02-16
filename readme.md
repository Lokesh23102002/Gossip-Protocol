# Gossip Protocol Over P2P Network
This project implements a peer-to-peer network in which there are n Seed nodes and many Peer Nodes

## Description
### Seed nodes
Seed nodes maintain the list of all the connected Peer nodes in the network.  
Each Peer node first connect to the seed node and get a list of connected peers.
### Peer nodes
Peer node are the end user which are connected to other peers and share information.  
They also check for the liveliness of other peer nodes and inform the Seed node about this.
## Working
### Seed Node And Peer Node working
when peer node start, it has to connect to n/2+1 seed node means just more than 50% of all seed nodes which ensure that each node get information about other peer nodes. 


### Seed Node and Peer Node Communication
The seed node and peer node communicate by passing various messages

## Shell commands
### Shell commands of Seeds
All the shell commands are case-insensitive  
To see the Peers connected you can use the command `Peers` in the command line of the Seed server.  
To exit write `exit` in the shell.

### Shell commands of Peers
- All the shell commands are case-insensitive
  - `Peers` to see all connected peers and also the recieved peer list from seed.
  - `Seeds` to see all the connected seeds.
  - `msg` to see all messages
  - `exit` to close the node and exit

## Gossip protocol Technicaleties.
### Seed Node and Peer Node Communication
The seed node and peer node communicate using following messages:
- Requests from peers
  - `ConnectSeed` This message is sent to Seed by peer for adding it to the network.
  - `RequestPL` This message is sent to recieve the peer list by peer.
  - `Death` This message is sent to seed to delete the unresponsive node.
- Response to peers
  - `ConnectedToSeed` This response is sent to Peer after connection request is accepted.
  - `PeerList` This response is sent to peer with the list of peers connected to the requested seed.

### Peer Node and Peer Node Communication
The peer node and peer node communicate using following messages:
- Requests 
  - `ConnectPeer` This message is sent by peer to connect to the nodes after recieving PeerList.
  - `Gossip` This message is sent with the gossip message format.
  
- Response
  - `ConnectedToPeer` This is message is sent when the connection request is accepted.

Other than these messages each peer node also send ping message to the connected peer nodes every 13seconds

## How to run
For this implementation we have used python 3.11.11 
There is a requirement.txt file first you have to install these requirements
After that make changes to config.csv with seed ip and port numbers  
After that start the seed nodes
  - `python seed.py --port <PORT_NUMBER> --max-peers <MAX_PEERS>` use this command to start all seed nodes

After that start the peers nodes
  - `python peer.py --port <PORT_NUMBER> --max-peers <MAX_PEERS>` use this command to start all peer nodes.

NOTE:- by default the ip used is the ip used by your PC (Host device).

For Testing purpose on windows device one can also use the `start_peer.bat` and `start_seed.bat` which autometically creates peers and seeds solving the problem to manually opening the terminals.




## Contributors
- [Lokesh Tanwar (B21EE035)]
- [Jatin Verma (B21EE028)]



