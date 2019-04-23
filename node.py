from blockchain import Blockchain
from uuid import uuid4
from verification import Verification

class Node:
    def __init__(self):
        # self.id = str(uuid4())
        self.id = 'AHMED'
        self.blockchain = Blockchain(self.id) # Generate a unique ID for each Node

    def get_transaction_value(self):
        """Returns the input of the user (a new transaction amount) as a float."""
        tx_recipient = input('Enter the recipient of the transaction: ')
        tx_amount = float(input("Your transaction amount please: "))
        return tx_recipient, tx_amount

    def get_user_choice(self):
        """Prompts the user for its choice an return it."""
        user_input = input('Your choice: ')
        return user_input

    def print_blockcahin_elements(self):
        """Output all blocks of the blockchain."""
        for block in self.blockchain.chain:
            print('Outputting Block')
            print(block)
        else:
            print('-'*20)

    def listen_for_input(self):
        waiting_for_input = True

        # A while loop for the user input interface
        # It's a loop that exists once waiting_for_input becomes False or when break is called
        while waiting_for_input:
            print('Please choose')
            print("1: Add a new transaction value")
            print('2: Mine a new block')
            print("3: Output the blockchain blocks")

            print('4: Check transaction validity')
            print("q: Exit loop")
            user_choice = self.get_user_choice()
            if user_choice == '1':
                tx_data = self.get_transaction_value()
                recipient, amount = tx_data
                # add transaction amount to blockchain
                if self.blockchain.add_transaction(recipient , self.id, amount=amount):
                    print('Added Transaction!')
                else:
                    print('Transaction Failed!')
                print('Open transactions')
                print(self.blockchain.get_open_transactions())

            elif user_choice == '2':
                self.blockchain.mine_block()

            elif user_choice == '3':
                self.print_blockcahin_elements()
            
            elif user_choice == '4':
                # Verify transactions

                if Verification.verify_transactions(self.blockchain.get_open_transactions(), self.blockchain.get_balance):
                    print('All transactions are valid!')
                else:
                    print('There are invalid transactions!')

            elif user_choice == 'q':
                # Quit
                waiting_for_input = False
            else:
                print('Input was invalid, please pick a value from the list!')
            
            if not Verification.verify_chain(self.blockchain.chain):
                # If chain cannot be verified quit loop
                self.print_blockcahin_elements()
                print('Invalid Blockchain!')
                break
            print('Balance of {}: {:6.2f}'.format(self.id, self.blockchain.get_balance())) # 6 digits and 2 decimal places

        else:
            print('User left')

        print('DONE!')

node = Node()
node.listen_for_input()