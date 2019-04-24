import json
import hashlib


def hash_string_256(string):
    """Create a SHA256 hash for a given input string.
    Arguments:
        :string: The string which should be hashed.
    """
    return hashlib.sha256(string).hexdigest()


def hash_block(block):
    """Hash a block and returns a string representation of it.
    
    Arguments:
        :block: The block that should be hashed
    """
    hashable_block = block.__dict__.copy()
    hashable_block['transactions'] = [tx.to_ordered_dict() for tx in hashable_block['transactions']]
    return hash_string_256(json.dumps(hashable_block, sort_keys=True).encode())