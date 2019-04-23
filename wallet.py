from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
import Crypto.Random
import binascii

class Wallet:
    def __init__(self):
        self.private_key = None
        self.public_key = None

    def create_keys(self):
        private_key, public_key = self.generate_keys()
        self.private_key = private_key
        self.public_key = public_key
        

    def load_keys(self):
        try:
            with open('wallet.txt', 'r') as f:
                keys = f.readlines()
                self.public_key = keys[0][:-1]
                self.private_key = keys[1]
        except (IOError, IndexError):
            print('WARNING! Loading wallet failed...')
    
    def save_keys(self):
        if self.public_key != None and self.private_key != None:
            try:
                with open('wallet.txt','w') as f:
                    f.write(self.public_key)
                    f.write('\n')
                    f.write(self.private_key)
            except (IOError, IndexError):
                print('WARNING! Saving wallet failed...')

    
    def generate_keys(self):
        private_key = RSA.generate(1024, Crypto.Random.new().read) # in binary
        public_key = private_key.publickey() # in binary
        return binascii.hexlify(private_key.exportKey(format='DER')).decode('ascii'), binascii.hexlify(public_key.exportKey(format='DER')).decode('ascii') # convert from binary to ascii

    def sign_transaction(self, sender, recipient ,amount):
        signer = PKCS1_v1_5.new(RSA.importKey(binascii.unhexlify(self.private_key))) # creating a signer identity
        h = SHA256.new((str(sender)+ str(recipient)+str(amount)).encode('utf8')) # create a hash
        signature = signer.sign(h)
        return binascii.hexlify(signature).decode('ascii') #return a string that contains the signature/ created when new transaction occurs
    @staticmethod
    def verify_transaction(transaction):
        
        public_key = RSA.importKey(binascii.unhexlify(transaction.sender))
        verifier = PKCS1_v1_5.new(public_key)
        h = SHA256.new((str(transaction.sender)+ str(transaction.recipient)+str(transaction.amount)).encode('utf8')) # create a hash
        return verifier.verify(h, binascii.unhexlify(transaction.signature))
        