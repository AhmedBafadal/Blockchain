"""Provides verification helper methods."""

from utility.hash_util import hash_string_256, hash_block
from wallet import Wallet

class Verification:
    """A helper class which offers various static and class-based verification and validation methods"""

    @staticmethod
    def valid_proof(transactions, last_hash, proof):
        """Validate a proof of work number and see if it solves the puzzle algorithm (two leading 0s)
        
        Arguments:
            :transactions: The Transactions of the block for which the proof is created.
            :last_hash: The previous block's hash which will be stored in the current block.
            : proof: The proof number tested."""
        # Create a string with all the hash inputs
        guess = (str([tx.to_ordered_dict() for tx in transactions]) + str(last_hash) +str(proof)).encode()
        # Hash string
        # NOTE: This is a different hash stored in the previous hash. Only used for proof of work algorithms.
        guess_hash = hash_string_256(guess)
        # Only a hash (based on the above inputs) which starts with two 0s is treated as valid.
        # Check if hash fulfills condition
        return guess_hash[0:2] == '00'
    
    @classmethod
    def verify_chain(cls, blockchain):
        """Verify the current blockchain and return True if its valid, False otherwise."""
        for index, block in enumerate(blockchain):
            if index == 0: # Dont need to validate the genesis block
                continue 
            if block.previous_hash != hash_block(blockchain[index -1]):
                return False
            if not cls.valid_proof(block.transactions[:-1], block.previous_hash, block.proof):
                print('Proof of work is invalid')
                return False
        return True
    
    @staticmethod
    def verify_transaction(transaction, get_balance, check_funds=True):
        """Verify a transaction by checking whether the sender has sufficient coins.
        
        Arguments:
            :transaction: The transaction that should be verified.
        """
        if check_funds:
            sender_balance = get_balance(transaction.sender)
            return sender_balance >= transaction.amount and Wallet.verify_transaction(transaction)
        else:
            return Wallet.verify_transaction(transaction)

    @classmethod
    def verify_transactions(cls, open_transactions, get_balance):
        """Check if all open transactions are valid"""
        return all([cls.verify_transaction(tx, get_balance, False) for tx in open_transactions]) # check if all open transactions are valid
    

