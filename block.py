from time import time
from printable import Printable

class Block(Printable):
    """Creating a block, where by every instance of the block will be independent, hence __init__"""
    def __init__(self, index, previous_hash, transactions, proof, timestamp=None):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = time() if timestamp is None else timestamp
        self.transactions = transactions
        self.proof = proof
