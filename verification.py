from hash_util import hash_string_256, hash_block

class Verification:
    
    @staticmethod
    def valid_proof(transactions, last_hash, proof):
        """Generates a new hash & checks if it fulfills the difficulty criteria"""
        guess = (str([tx.to_ordered_dict() for tx in transactions]) + str(last_hash) +str(proof)).encode()
        guess_hash = hash_string_256(guess)
        print(guess_hash)
        # Check if hash fulfills condition
        return guess_hash[0:2] == '00'
    
    @classmethod
    def verify_chain(cls, blockchain):
        """Verify the current blockchain and return True if its valid, False otherwise"""
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
    def verify_transaction(transaction, get_balance):
        """Verify a transaction by checking whether the sender has sufficient coins.
        
        Arguments:
            :transaction: The transaction that should be verified.
        """
        sender_balance = get_balance()
        return sender_balance >= transaction.amount

    @classmethod
    def verify_transactions(cls, open_transactions, get_balance):
        """Check if all open transactions are valid"""
        return all([cls.verify_transaction(tx, get_balance) for tx in open_transactions]) # check if all open transactions are valid
    

