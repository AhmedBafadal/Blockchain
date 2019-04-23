import functools
import hashlib
from collections import OrderedDict
from hash_util import hash_string_256, hash_block
import json
import pickle

from block import Block
from transaction import Transaction

# Reward given to miners for creating a new block
MINING_REWARD = 10

# Initializing empty blockchain list
blockchain = []
# Unhandled transactions
open_transactions = []
# Owner of blockchain node, hence is the identifier
owner = 'Ahmed'
# Registered participants: Nodes sending/ recieving coins
participants = {'Ahmed'}

def load_data():
    global blockchain
    global open_transactions
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
                converted_tx = [OrderedDict(
                            [('sender', tx['sender']), ('recipient', tx['recipient']), ('amount',tx['amount'])]) for tx in block['transactions']] #creating an ordered dict for each transaction
                updated_block = Block(block['index'], block['previous_hash'], converted_tx, block['proof'], block['timestamp'])
                
                updated_blockchain.append(updated_block)
                
            blockchain = updated_blockchain
            open_transactions = json.loads(file_content[1])
            updated_transactions = []
            for tx in open_transactions:
                updated_transaction = OrderedDict(
                            [('sender', tx['sender']), ('recipient', tx['recipient']), ('amount',tx['amount'])])
                updated_transactions.append(updated_transaction)
            open_transactions = updated_transactions
    except IOError:
        # Starting block for the blockchain
        genesis_block = Block(0,'',[],100, 0)
        
        # Initializing empty blockchain list with genesis block
        blockchain = [genesis_block]
        # Unhandled transactions
        open_transactions = []


load_data()

def save_data():
    try:
        with open('blockchain.txt', mode='w') as f:
            saveable_chain = [block.__dict__ for block in blockchain]
            f.write(json.dumps(saveable_chain))
            f.write('\n')
            f.write(json.dumps(open_transactions))
            # save_data = {
            #     'chain':blockchain,
            #     'ot': open_transactions
            # }
            # f.write(pickle.dumps(save_data))
    except (IOError, IndexEerror):
        print('WARNING! Saving Failed!')


def valid_proof(transactions, last_hash, proof):
    """Generates a new hash & checks if it fulfills the difficulty criteria"""
    guess = (str(transactions) + str(last_hash) +str(proof)).encode()
    guess_hash = hash_string_256(guess)
    print(guess_hash)
    # Check if hash fulfills condition
    return guess_hash[0:2] == '00'

def proof_of_work():
    last_block = blockchain[-1]
    last_hash = hash_block(last_block)
    proof = 0
    while not valid_proof(open_transactions, last_hash, proof):
        proof += 1
    return proof



def get_balance(participant):
    """Calculate and return the balance for a participant.
    
    Arguments:
        :participant: The person for whom to calculate the balance.
    """
    # Fetch a list of all sent coin amounts for the given person (empty lists are returned if the person was NOT the sender)
    # This fetches sent amounts of transactions that were already included in blocks of the blockchain
    tx_sender = [[tx['amount'] for tx in block.transactions if tx['sender'] == participant] for block in blockchain]
    # Fetch a list of all sent coin amounts for the given person (empty lists are returned if the person was NOT the sender)
    # This fetches sent amounts of open transactions (to avoid double spending)
    open_tx_sender = [tx['amount'] for tx in open_transactions if tx['sender'] == participant]
    tx_sender.append(open_tx_sender)
    print(tx_sender)
    # Calculate the total amount of coins sent
    amount_sent = functools.reduce(lambda tx_sum, tx_amt: tx_sum+ sum(tx_amt) if len(tx_amt) > 0 else tx_sum+0, tx_sender, 0)

    # This fetches recieved coin amounts of transactions that were already included in blocks of the blockchain
    # Open transactions are ignored here because one should not be able to spend coins before the transaction was confirmed + included in a block
    tx_recipient = [[tx['amount'] for tx in block.transactions if tx['recipient'] == participant] for block in blockchain]

    amount_recieved = functools.reduce(lambda tx_sum, tx_amt: tx_sum+ sum(tx_amt) if len(tx_amt) > 0 else tx_sum+0, tx_recipient, 0)

    # Return the total balance
    return amount_recieved - amount_sent


def get_last_blockchain_value():
    """Returns the last value of the current blockchain"""
    if len(blockchain) < 1:
        return None
    return blockchain[-1]


def verify_transaction(transaction):
    """Verify a transaction by checking whether the sender has sufficient coins.
    
    Arguments:
        :transaction: The transaction that should be verified.
    """
    sender_balance = get_balance(transaction['sender'])
    return sender_balance >= transaction['amount']

def verify_transactions():
    """Check if all open transactions are valid"""
    return all([verify_transaction(tx) for tx in open_transactions]) # check if all open transactions are valid

def add_transaction(recipient, sender=owner, amount=1.0):
    """Append new value as well as the last blockchain value to the blockchain
    Arguments:
        :sender: Sender of coins in transaction.
        :recipient: Reciever of coins in transaction
        :amount: Amount of coins sent in transaction (default = 1.0)
    """
    # transaction = {'sender':sender, 
    #     'recipient':recipient, 
    #     'amount':amount}
    transaction = OrderedDict([('sender', sender), ('recipient', recipient), ('amount',amount)])
    if verify_transaction(transaction):
        open_transactions.append(transaction)
        participants.add(sender)
        participants.add(recipient)
        save_data()
        return True
    return False


def mine_block():
    """Create a new block and add open transactions to it."""
    # Fetch the currently last block of the blockchain
    last_block = blockchain[-1]
    # Hash the last block (=> to be able to compare it to the stored hash value)
    hashed_block = hash_block(last_block)
    proof = proof_of_work()
    # Miners should be rewarded, so let's create a reward transaction
    # reward_transaction = {
    #     'sender':'MINING',
    #     'recipient':owner,
    #     'amount': MINING_REWARD
    # }
    reward_transaction = OrderedDict([('sender','MINING'),('recipient',owner),('amount',MINING_REWARD)])
    # Copy transaction instead of manipulating the original open_transactions list
    # This ensures that if mining should fail, the reward transaction would be prevented from being stored in the open transactions
    copied_transactions = open_transactions[:]
    copied_transactions.append(reward_transaction) # adding mined block to system

    block = Block(len(blockchain), hashed_block, copied_transactions, proof)
    blockchain.append(block)
    
    return True



def get_transaction_value():
    """Returns the input of the user (a new transaction amount) as a float."""
    tx_recipient = input('Enter the recipient of the transaction: ')
    tx_amount = float(input("Your transaction amount please: "))
    return tx_recipient, tx_amount

def get_user_choice():
    """Prompts the user for its choice an return it."""
    user_input = input('Your choice: ')
    return user_input

def print_blockcahin_elements():
    """Output all blocks of the blockchain."""
    for block in blockchain:
        print('Outputting Block')
        print(block)
    else:
        print('-'*20)

def verify_chain():
    """Verify the current blockchain and return True if its valid, False otherwise"""
    for index, block in enumerate(blockchain):
        if index == 0: # Dont need to validate the genesis block
            continue 
        if block.previous_hash != hash_block(blockchain[index -1]):
            return False
        if not valid_proof(block.transactions[:-1], block.previous_hash, block.proof):
            print('Proof of work is invalid')
            return False
    return True


waiting_for_input = True


# A while loop for the user input interface
# It's a loop that exists once waiting_for_input becomes False or when break is called

while waiting_for_input:
    print('Please choose')
    print("1: Add a new transaction value")
    print('2: Mine a new block')
    print("3: Output the blockchain blocks")
    print('4: Output participants of the blockchain')
    print('5: Check transaction validity')

    print("q: Exit loop")
    user_choice = get_user_choice()
    if user_choice == '1':
        tx_data = get_transaction_value()
        recipient, amount = tx_data
        # add transaction amount to blockchain
        if add_transaction(recipient, amount=amount):
            print('Added Transaction!')
        else:
            print('Transaction Failed!')
        print('Open transactions')
        print(open_transactions)

    elif user_choice == '2':
        if mine_block():
            # Reset open transactions once block mined
            open_transactions = []
            save_data()

    elif user_choice == '3':
        print_blockcahin_elements()
    
    elif user_choice == '4':
        # Output all participants in blockchain
        print(participants)
    
    elif user_choice == '5':
        # Verify transactions
        if verify_transactions():
            print('All transactions are valid!')
        else:
            print('There are invalid transactions!')

    elif user_choice == 'q':
        # Quit
        waiting_for_input = False
    else:
        print('Input was invalid, please pick a value from the list!')
    if not verify_chain():
        # If chain cannot be verified quit loop
        print_blockcahin_elements()
        print('Invalid Blockchain!')
        break
    print('Balance of {}: {:6.2f}'.format(owner, get_balance('Ahmed'))) # 6 digits and 2 decimal places


else:
    print('User left')
        




print('DONE!')