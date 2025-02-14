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
To see the Peers connected you can use the command `Peer` in the command line of the Seed server.

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
  - `Connect` This message is sent to Seed by peer for adding it to the network.
  - `RequestPL` This message is sent to recieve the peer list by peer.
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
  
## How to run


## Contributors
- [Lokesh Tanwar (B21EE035)]
- [Jatin Verma (B21EE028)]



