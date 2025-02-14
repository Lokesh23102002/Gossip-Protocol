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
### How to see All the connected Peers on a Seed
To see the Peers connected you can use the command `Peer` in the command line of the Seed server.

### How to see All the connected Peers and Seeds on a Peer
- To see the list of connected seeds and peers  on a Peer server you can enter following commands in the command line of the Peer.
  - `Peers` to see all connected peers and also the recieved peer list from seed.
  - `Seeds` to see all the connected seeds.

### How to see the message sent and received by peer nodes.

## Gossip protocol Technicaleties.


## How to run


## Contributors
- [Lokesh Tanwar (B21EE035)]
- [Jatin Verma (B21EE029)]



