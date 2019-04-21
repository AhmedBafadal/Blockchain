# Initializing blockchain list
blockchain = []
open_transactions = []
owner = 'Ahmed'

def get_last_blockchain_value():
    """Returns the last value of the current blockchain"""
    if len(blockchain) < 1:
        return None
    return blockchain[-1]


def add_transaction( recipient, sender=owner, amount=1.0):
    """Append new value as well as the last blockchain value to the blockchain
    Arguments:
        :sender: Sender of coins in transaction.
        :recipient: Reciever of coins in transaction
        :amount: Amount of coins sent in transaction (default = 1.0)
    """
    transaction = {'sender':sender, 
        'recipient':recipient, 
        'amount':amount}

    open_transactions.append(transaction)
    

def mine_block():
    pass



def get_transaction_value():
    """Returns the input of the user (a new transaction amount) as a float."""
    
    tx_recipient = input('Enter the recipient of the transaction: ')
    tx_amount = float(input("Your transaction amount please: "))
    return tx_recipient, tx_amount

def get_user_choice():
    user_input = input('Your choice: ')
    return user_input

def print_blockcahin_elements():
    for block in blockchain:
        print(block)

def verify_chain():
    # block_index = 0
    is_valid = True #Helper variable
    for block_index in range(len(blockchain)): 
        if block_index == 0:
            continue
        if blockchain[block_index][0] == blockchain[block_index-1]:
            #Check if the first element of the second block is equal to entire previous block
            is_valid = True
        else:
            is_valid = False
            break
            block_index += 1
    return is_valid




waiting_for_input = True
while waiting_for_input:
    print('Please choose')
    print("1: Add a new transaction value")
    print("2: Output the blockchain blocks")
    print("h: Manipulate the chain")
    print("q: Exit loop")
    user_choice = get_user_choice()
    if user_choice == '1':
        tx_data = get_transaction_value()
        recipient, amount = tx_data
        # add transaction amount to blockchain
        add_transaction(recipient, amount=amount)
        print('Open transactions')
        print(open_transactions)

    elif user_choice == '2':
        print_blockcahin_elements()
    elif user_choice == 'h':
        if len(blockchain) >= 1:
            blockchain[0] = [2]
    elif user_choice == 'q':
        waiting_for_input = False
    else:
        print('Input was invalid, please pick a value from the list!')
    if not verify_chain():
        print_blockcahin_elements()
        print('Invalid Blockchain!')
        break


else:
    print('User left')
        




print('DONE!')