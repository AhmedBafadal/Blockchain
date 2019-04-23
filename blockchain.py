import functools
import hashlib
from collections import OrderedDict
import json
import pickle
from utility.hash_util import hash_block
from utility.verification import Verification
from block import Block
from transaction import Transaction




# Reward given to miners for creating a new block
MINING_REWARD = 10

class Blockchain:
    def __init__(self, hosting_node_id):
        # Starting block for the blockchain
        genesis_block = Block(0,'',[],100, 0)
        # Initializing empty blockchain list
        self.chain = [genesis_block]
        # Unhandled transactions
        self.__open_transactions = []
        self.hosting_node = hosting_node_id
        self.load_data()
    
    @property
    def chain(self):
        return self.__chain[:]
  
    @chain.setter
    def chain(self, val):
        self.__chain = val
    
    def get_open_transactions(self):
        return self.__open_transactions[:]





    def load_data(self):
        """Initialize blockchain + open transactions data from a file."""
        try:
            with open('blockchain.txt', mode='r') as f:
                # file_content = pickle.loads(f.read())
                # print(file_content)
                file_content = f.readlines()
                # blockchain = file_content['chain']
                # open_transactions = file_content['ot']
                # # First line is blockchain, Second is transaction data
                blockchain = json.loads(file_content[0][:-1]) #avoid \n character
                updated_blockchain = []
                for block in blockchain:
                    converted_tx = [Transaction(tx['sender'], tx['recipient'],tx['signature'] , tx['amount']) for tx in block['transactions']]
                    
                    updated_block = Block(block['index'], block['previous_hash'], converted_tx, block['proof'], block['timestamp'])
                    
                    updated_blockchain.append(updated_block)
                    
                self.chain = updated_blockchain # access without double underscore to trigger property setter
                open_transactions = json.loads(file_content[1])
                updated_transactions = []
                for tx in open_transactions:
                    updated_transaction = Transaction(tx['sender'], tx['recipient'],tx['signature'] , tx['amount'])
                    updated_transactions.append(updated_transaction)
                self.__open_transactions = updated_transactions
        except (IOError, IndexError):
            pass


    def save_data(self):
        """Save Blockchain + open transaction snapshot to a file."""
        try:
            with open('blockchain.txt', mode='w') as f:
                saveable_chain = [block.__dict__ for block in [Block(block_el.index, block_el.previous_hash, [tx.__dict__ for tx in block_el.transactions] ,block_el.proof, block_el.timestamp) for block_el in self.__chain]]
                f.write(json.dumps(saveable_chain))
                f.write('\n')
                saveable_tx = [tx.__dict__ for tx in self.__open_transactions]
                f.write(json.dumps(saveable_tx))
                # save_data = {
                #     'chain':blockchain,
                #     'ot': open_transactions
                # }
                # f.write(pickle.dumps(save_data))
        except (IOError, IndexError):
            print('WARNING! Saving Failed!')



    def proof_of_work(self):
        last_block = self.__chain[-1]
        last_hash = hash_block(last_block)
        proof = 0

        while not Verification.valid_proof(self.__open_transactions, last_hash, proof):
            proof += 1
        return proof



    def get_balance(self):
        """Calculate and return the balance for a participant.
        """
        participant = self.hosting_node
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

        # This fetches recieved coin amounts of transactions that were already included in blocks of the blockchain
        # Open transactions are ignored here because one should not be able to spend coins before the transaction was confirmed + included in a block
        tx_recipient = [[tx.amount for tx in block.transactions if tx.recipient == participant] for block in self.__chain]

        amount_recieved = functools.reduce(lambda tx_sum, tx_amt: tx_sum+ sum(tx_amt) if len(tx_amt) > 0 else tx_sum+0, tx_recipient, 0)

        # Return the total balance
        return amount_recieved - amount_sent


    def get_last_blockchain_value(self):
        """Returns the last value of the current blockchain"""
        if len(self.__chain) < 1:
            return None
        return self.__chain[-1]


    def add_transaction(self, recipient, sender, signature, amount=1.0):
        """Append new value as well as the last blockchain value to the blockchain
        Arguments:
            :sender: Sender of coins in transaction.
            :recipient: Reciever of coins in transaction
            :amount: Amount of coins sent in transaction (default = 1.0)
        """
        # transaction = {'sender':sender, 
        #     'recipient':recipient, 
        #     'amount':amount}
        if self.hosting_node == None:
            return False
        transaction = Transaction(sender, recipient, signature, amount)
        
        if Verification.verify_transaction(transaction, self.get_balance):
            self.__open_transactions.append(transaction)
            self.save_data()
            return True
        return False


    def mine_block(self):
        """Create a new block and add open transactions to it."""
        if self.hosting_node == None:
            return False
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
        
        reward_transaction = Transaction('MINING', self.hosting_node, '' ,MINING_REWARD)
        # Copy transaction instead of manipulating the original open_transactions list
        # This ensures that if mining should fail, the reward transaction would be prevented from being stored in the open transactions
        copied_transactions = self.__open_transactions[:]
        copied_transactions.append(reward_transaction) # adding mined block to system

        block = Block(len(self.__chain), hashed_block, copied_transactions, proof)
        self.__chain.append(block)
        self.__open_transactions = []
        self.save_data()
        
        return True
