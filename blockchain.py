import functools
import hashlib
from collections import OrderedDict
import json
import pickle
import requests
from utility.hash_util import hash_block
from utility.verification import Verification
from block import Block
from transaction import Transaction
from wallet import Wallet




# Reward given to miners for creating a new block
MINING_REWARD = 10

class Blockchain:
    """The Blockchain class manages the chain of blocks as well as open transactions and the node on which it's running.

    Attributes:
        :chain: The list of blocks.
        :open_transactions (private): The list of open transactions.
        :public_key: The connected node (which runs the blockchain).
    
    """
    def __init__(self, public_key,node_id):
        """Constructor of the Blockchain class."""
        # Starting block for the blockchain
        genesis_block = Block(0,'',[],100, 0)
        # Initializing empty blockchain list
        self.chain = [genesis_block]
        # Unhandled transactions
        self.__open_transactions = []
        self.public_key = public_key
        self.__peer_nodes = set()
        self.node_id = node_id
        self.resolve_conflicts = False
        self.load_data()
    
    @property
    def chain(self):
        """Convert the chain attribute into a property with a getter and setter"""
        return self.__chain[:]
  
    @chain.setter
    def chain(self, val):
        """Setter of chain property"""
        self.__chain = val
    
    def get_open_transactions(self):
        """Returns a copy of the open transactions list."""
        return self.__open_transactions[:]

    def load_data(self):
        """Initialize blockchain + open transactions data from a file."""
        try:
            with open('blockchain-{}.txt'.format(self.node_id), mode='r') as f:
                # file_content = pickle.loads(f.read())
                file_content = f.readlines()
                # blockchain = file_content['chain']
                # open_transactions = file_content['ot']
                # # First line is blockchain, Second is transaction data
                blockchain = json.loads(file_content[0][:-1]) #avoid \n character
                # Need to convert the loaded data because Transactions should use an Ordered Dict
                updated_blockchain = []
                for block in blockchain:
                    converted_tx = [Transaction(tx['sender'], tx['recipient'],tx['signature'] , tx['amount']) for tx in block['transactions']]
                    
                    updated_block = Block(block['index'], block['previous_hash'], converted_tx, block['proof'], block['timestamp'])
                    updated_blockchain.append(updated_block)
                    
                self.chain = updated_blockchain # access without double underscore to trigger property setter
                open_transactions = json.loads(file_content[1][:-1])
                # Need to convert the loaded data because Transactions should use an Ordered Dict
                updated_transactions = []
                for tx in open_transactions:
                    updated_transaction = Transaction(tx['sender'], tx['recipient'],tx['signature'] , tx['amount'])
                    updated_transactions.append(updated_transaction)
                self.__open_transactions = updated_transactions
                peer_nodes = json.loads(file_content[2])
                self.__peer_nodes = set(peer_nodes)
        except (IOError, IndexError):
            pass


    def save_data(self):
        """Save Blockchain + open transaction snapshot to a file."""
        try:
            with open('blockchain-{}.txt'.format(self.node_id), mode='w') as f:
                saveable_chain = [block.__dict__ for block in [Block(block_el.index, block_el.previous_hash, [tx.__dict__ for tx in block_el.transactions] ,block_el.proof, block_el.timestamp) for block_el in self.__chain]]
                f.write(json.dumps(saveable_chain))
                f.write('\n')
                saveable_tx = [tx.__dict__ for tx in self.__open_transactions]
                f.write(json.dumps(saveable_tx))
                f.write('\n')
                f.write(json.dumps(list(self.__peer_nodes)))
                # save_data = {
                #     'chain':blockchain,
                #     'ot': open_transactions
                # }
                # f.write(pickle.dumps(save_data))
        except (IOError, IndexError):
            print('WARNING! Saving Failed!')



    def proof_of_work(self):
        """Generate a proof of work for the open transactions, the hash of the previous block and a random number (which is guessed until it fits)"""
        last_block = self.__chain[-1]
        last_hash = hash_block(last_block)
        proof = 0
        # Try different PoW numbers and return the first valid one
        while not Verification.valid_proof(self.__open_transactions, last_hash, proof):
            proof += 1
        return proof



    def get_balance(self, sender=None):
        """Calculate and return the balance for a participant.
        """
        if sender is None:
            if self.public_key is None:
                return None
            participant = self.public_key
        else:
            participant = sender
        # Fetch a list of all sent coin amounts for the given person (empty lists are returned if the person was NOT the sender)
        # This fetches sent amounts of transactions that were already included in blocks of the blockchain
        tx_sender = [[tx.amount for tx in block.transactions if tx.sender == participant] for block in self.__chain]
        # Fetch a list of all sent coin amounts for the given person (empty lists are returned if the person was NOT the sender)
        # This fetches sent amounts of open transactions (to avoid double spending)
        open_tx_sender = [tx.amount for tx in self.__open_transactions if tx.sender == participant]
        tx_sender.append(open_tx_sender)
        print(tx_sender)
        # Calculate the total amount of coins sent
        amount_sent = functools.reduce(lambda tx_sum, tx_amt: tx_sum+ sum(tx_amt) if len(tx_amt) > 0 else tx_sum+0, tx_sender, 0)

        # This fetches received coin amounts of transactions that were already included in blocks of the blockchain
        # Open transactions are ignored here because one should not be able to spend coins before the transaction was confirmed + included in a block
        tx_recipient = [[tx.amount for tx in block.transactions if tx.recipient == participant] for block in self.__chain]

        amount_received = functools.reduce(lambda tx_sum, tx_amt: tx_sum+ sum(tx_amt) if len(tx_amt) > 0 else tx_sum+0, tx_recipient, 0)

        # Return the total balance
        return amount_received - amount_sent


    def get_last_blockchain_value(self):
        """Returns the last value of the current blockchain"""
        if len(self.__chain) < 1:
            return None
        return self.__chain[-1]


    def add_transaction(self, recipient, sender, signature, amount=1.0, is_receiving=False):
        """Append new value as well as the last blockchain value to the blockchain

        Arguments:
            :sender: Sender of coins in transaction.
            :recipient: Receiver of coins in transaction.
            :amount: Amount of coins sent in transaction (default = 1.0)
        """
        # transaction = {'sender':sender, 
        #     'recipient':recipient, 
        #     'amount':amount}
        # if self.public_key == None:
        #     return False
        transaction = Transaction(sender, recipient, signature, amount)
        if Verification.verify_transaction(transaction, self.get_balance):
            self.__open_transactions.append(transaction)
            self.save_data()
            if not is_receiving:
                # Only broadcasting to peer nodes if on the original node that created the transaction. 
                # This prevents a chain of infinite requests occuring and only getting back one response
                for node in self.__peer_nodes:
                    # send an http request to communicate with the nodes
                    url = 'http://{}/broadcast-transaction'.format(node)
                    try:
                        response = requests.post(url, json={'sender': sender, 'recipient': recipient, 'amount':amount, 'signature': signature})
                        if response.status_code == 400 or response.status_code == 500:
                            print('Transaction declined, needs resolving.')
                            return False
                    except requests.exceptions.ConnectionError:
                        continue # in case could not broadcast to node (e.g. no internet) skip to the next node
            return True
        return False


    def mine_block(self):
        """Create a new block and add open transactions to it."""
        if self.public_key is None:
            return None
        # Fetch the currently last block of the blockchain
        last_block = self.__chain[-1]
        # Hash the last block (=> to be able to compare it to the stored hash value)
        hashed_block = hash_block(last_block)
        proof = self.proof_of_work()
        # Miners should be rewarded, so let's create a reward transaction
        # reward_transaction = {
        #     'sender':'MINING',
        #     'recipient':owner,
        #     'amount': MINING_REWARD
        # }
        
        reward_transaction = Transaction('MINING', self.public_key, '' ,MINING_REWARD)
        # Copy transaction instead of manipulating the original open_transactions list
        # This ensures that if mining should fail, the reward transaction would be prevented from being stored in the open transactions
        copied_transactions = self.__open_transactions[:]
        for tx in copied_transactions:
            if not Wallet.verify_transaction(tx):
                return None
        copied_transactions.append(reward_transaction) # adding mined block to system
        block = Block(len(self.__chain), hashed_block, copied_transactions, proof)

        self.__chain.append(block)
        self.__open_transactions = []
        self.save_data()
        ## Broadcast 
        for node in self.__peer_nodes:
            url = 'http://{}/broadcast-block'.format(node)
            converted_block = block.__dict__.copy()
            converted_block['transactions'] = [tx.__dict__ for tx in converted_block['transactions']]
            try:
                response = requests.post(url, json={'block': converted_block})
                if response.status_code == 400 or response.status_code == 500:
                    print('Block declined, needs resolving.')
                if response.status_code == 409:
                    self.resolve_conflicts = True
            except requests.exceptions.ConnectionError:
                continue
        return block

    def add_block(self, block):
        # Validate block, check pow and store
        # Must convert transactions to a list, because verification expects data in that format. <dictionary to a list of transaction objects>
        transactions = [Transaction(tx['sender'], tx['recipient'], tx['signature'], tx['amount']) for tx in block['transactions']]
        proof_is_valid = Verification.valid_proof(transactions[:-1], block['previous_hash'], block['proof'])#Passing in a list of all transactions of block being received when validating pow. 
        #Avoid last block in chain as it contains the reward transaction and will invalidate it. 
        # #Usually calculate pow before adding reward transaction (e.g. mine_block). 
        # using [:-1] avoids using the reward transaction as part of the transactions used to validate the incoming pow which wont work.
        hashes_match = hash_block(self.chain[-1]) == block['previous_hash'] 
        if not proof_is_valid or not hashes_match:
            return False
        converted_block = Block(block['index'], block['previous_hash'], transactions, block['proof'], block['timestamp'])
        self.__chain.append(converted_block)
        stored_transactions = self.__open_transactions[:]
        for itx in block['transactions']:
            for opentx in stored_transactions:
                # if all fields are equal it is the same transaction
                if opentx.sender == itx['sender'] and opentx.recipient == itx['recipient'] and opentx.amount == itx['amount'] and opentx.signature == itx['signature']:
                    try:
                        self.__open_transactions.remove(opentx)
                    except ValueError:
                        print('Item was already removed.')
        self.save_data()
        return True


    def resolve(self):
        winner_chain = self.chain
        replace = False ## Control whether current chain is being replaced
        # Get a snapshot of blockcahin on every peer node to check which peer node has which blockchain & which one is correct.
        for node in self.__peer_nodes:
            url = 'http://{}/chain'.format(node)
            try:
                response = requests.get(url)
                node_chain = response.json()
                node_chain = [Block(block['index'], block['previous_hash'], [Transaction(tx['sender'], tx['recipient'], tx['signature'], tx['amount']) for tx in block['transactions']], block['proof'], block['timestamp']) for block in node_chain]
                
                node_chain_length = len(node_chain)
                local_chain_length = len(winner_chain)
                if node_chain_length > local_chain_length and Verification.verify_chain(node_chain):
                    # if chain of peer node is longer and valid, use it as local chain
                    winner_chain = node_chain
                    replace = True
            except requests.exceptions.ConnectionError:
                continue # avoids break down code for node offline that cant be reached
        self.resolve_conflicts = False
        self.chain = winner_chain
        if replace:
            self.__open_transactions = []
        self.save_data()
        return replace

    def add_peer_node(self, node):
        """Adds a new node to the peer node set.
        Arguments:
            :node: The node URL which should be added.
        """
        self.__peer_nodes.add(node)
        self.save_data()
    

    def remove_peer_node(self, node):
        """Removes a node from the peer node set.
        Arguments:
            :node: The node URL which should be added.
        """
        self.__peer_nodes.discard(node)
        self.save_data()
    

    def get_peer_nodes(self):
        """Return a list of all connected peer nodes"""
        return list(self.__peer_nodes)
    