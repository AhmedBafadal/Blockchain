# Blockchain App


## Description
This project is a simplified blockchain and cryptocurrency application, built using **Flask**, **Flask CORS** & **PyCryptodome**.  

 The app developed is inherently a system in which a record of transactions made in a native cryptocurrency is maintained across several nodes linked together in a peer-to-peer network via HTTP. 
 
 Each node operates as a wallet which enables users to unqiuely identify themselves via public key and send coins through transactions to other wallets using a private key to sign each transaction. This app also implements consensus algorithms to resolve conflicts arising from multiple nodes sharing different kinds of information (e.g. having blockchains of different lengths).  
 
 Any transactions created are broadcast to all other nodes in distributed network who will verify the transaction to ensure there are sufficient funds available and validate the node's identity. This broadcast capability also exists for new blocks created via mining, in order for every other node to be made aware of the addition to the chain and validate it.

### How is the Blockchain built?
 Within each block of the blockchain consists a list of transactions, and to prevent the manipulation of data in blocks within this distributed network, each block is hashed using the respective block's metadata and stored in the next block in the blockchain. As such, changes to any previous blocks will not match the recalculated hash for the updated data in the next block (e.g. Same Input == Same Output).

### How does the cryptocurrency work?
 The cryptocurrency developed within this project employs encryption techniques used to regulate the generation of units of currency and verify the transfer of funds. The coins that form this cryptocurrency are created via Mining, which is how new blocks are added. Transactions between nodes are initially stored as Open Transactions, and to be confirmed as valid, such transactions must be included in a new block which is added at the end of the blockchain. 
 
 Member nodes who add this are 'Mining' since this process takes longer due to the requirement to solve a complex 'proof of work' algorithm to gain new coins from the system as a reward.



## Implementation
Upon running app, users can create a new wallet (saved as wallet-<PORT_NUMBER>.txt), which generates a unique public key & private key which will hold all the user's coins. Users can also mine coins and send funds to other wallets in the network provided the sender has the public key of the recipient and funds available.

**Important!** Before any transactions can occur, users seeking to send coins must access the network tab, and add the url of the target node into the network to be identified. Any existing nodes in the network can be viewed by clicking the 'Load Peer Nodes' button.

Please note, any transactions sent between parties will not be directly added into the recipient's funds and instead will be stored as an open transaction until a new block is created/mined. As such, inbound funds can be viewed by the recipient through accessing the 'Open Transactions' tab and clicking 'Load Transactions'. Once a new block is created, open transactions is emptied and the recipient officially recieves the funds in the account.

Should any conflicts occur in blockchain versions across multiple nodes please click the 'Resolve Conflicts' button to implement consensus capability.

Users can also view the entire blockchain in the 'Blockchain' tab by clicking the 'Load Blockchain' button.

### Managing & Resetting the Wallet and Blockchain

A copy of the entire blockchain is stored in each node (saved as blockchain-<PORT_NUMBER>.txt). Please note, deleting this file will reset the wallet funds and blockchain, but not delete the wallet itself. However, deleting wallet-<PORT_NUMBER>.txt files will delete the entire wallet and will require the creation of a new one.

### Transaction workflow:

1. Create/Load wallet for sender and recipient.
2. Add recipient node into network (using any portnumber)
3. Mine coin for funds
4. Send desired funds to recipient node using their public key (Once sent this should be available as an Open Transaction on both nodes)
5. Mine coins (This adds all open transactions to the blockchain and into recipient's funds)
6. Load wallet on recipient node


## Installation

```
pip install -r requirements.txt

* Note: Command below runs app with default port=5000, to addport use -p=<DESIRED_PORT_NUMBER>

python node.py

* In Second Terminal:

python node.py -p=5001

```


## Limitations
This blockchain is not yet production ready due to several factors.  

Most noteably:

    * Error Handling: needs improvement for different types errors. (Only accounted for nodes that may be offline during broadcasts)

    * Scalability: Blockchain stored in a list and as text file. Bigger blockchain gets requires more memory to load & process and the more the nodes need to download

    * Bandwidth costs: Downloading the entire chain will have significant costs as chain grows, in the 'resolve' function it querys all other       nodes to obtain the complete chain from each node. This is not applicable in production and need to validate the chain without  obtaining entire chain.

    * Peer Network: Broadcasting works but requires scheduled broadcasting or asyncronous broadcasting in a real blockchain. 
    This is becuase in 'mine_block' method in 'blockchain.py' all peer nodes are contacted to be informed of the new block, but these peer nodes should also contact their peer nodes to let them know. But this was deliberately left out (in 'add_transaction' method in 'blockchain.py' there is a flag 'is_receiving=False') this is the same for incoming transactions. This is done because the danger is this leads to very long chain of informing other nodes which inform other nodes etc. It is not practical to wait for all responses as the original node mining the block.  


## Next Steps
Next steps to tackle limitations:  

    * Scalability: Store in postgresql database instead of text

    * Scalability: Load only parts of the blockchain into memory (requires recalibration of calculation of funds and validation of chain)

    * Broadcasting: To solve the limitations in broadcasting, need to develop a scheduling task where information is sent out to peer nodes and there is no need to wait for a response, but query them at a later point in time or set up a web socket connection (live connection between peers and not a push connection as in this project).

    * Mining Difficulty: Mining occurs by generating a new block via proof of work, but the difficulty can be increased dynamically based on        the length of the blockchain and coins in circulation (e.g. first few blocks added quickly but as blockchain grows and the more coins   are in the system, the longer it should take to mine a new block)

    * Merkle Tree: For validating and analysing transactions could look into using a Merkle Tree. Currently in this project, transactions are       verified by going through all transactions in all blocks which are individually verified. For significantly larger transaction              volumes in each block, this will be highly resource intensive. Merkle tree can be a more efficient manner of hashing the verified           transactions and to easily validate if that hash is correct and therefore validate your transactions in bulk.



