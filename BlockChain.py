import hashlib
import datetime as date
import json
from urllib.parse import urlparse
import requests

class BlockChain():

    def __init__(self):
        self.current_transactions = []
        self.chain = []
        self.nodes = set()
        self.create_block(previous_hash=1,proof=100)

    def create_block(self,previous_hash,proof):
        """
        Create a new Block in the Blockchain
        :param previous_hash: (Optional) <str> Hash of previous Block
        :param proof: <int> The proof given by the Proof of Work algorithm
        :return: <dict> New Block
        """

        block = {
            "index": len(self.chain)+1,
            "timestamp":str(date.datetime.now()), 
            "transactions" : self.current_transactions,
            "proof" : proof,
            "prev_hash" : previous_hash or self.hash(self.chain[-1])
        }

        self.current_transactions = []
        self.chain.append(block)
        return block
    
    def new_transaction(self,sender,recipient,amount):
        """
        Create a new transaction to go into the next mined Block
        :param sender: <str> Address of the sender
        :param sender: <str> Address of the recipient
        :param sender: <int> Amount
        :return sender: <int> The index of the block that will hold this transaction
        """
        self.current_transactions.append({
            'sender':sender,
            'recipient':recipient,
            'amount':amount
        })
        return self.last_block['index']+1

    @property
    def last_block(self):
        return self.chain[-1]
    
    def hash(self,block):
        """
        Creates a SHA-256 hash of a Block

        :param block: <dict> Block
        :return <str>
        """
        
        # ordering the dict for consistent hash
        block_string = json.dumps(block,sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
    
    def proof_of_work(self):
        """
        Simple Proof of Work Algorithm
        - Find a number 'p' such that hash(pp') contains leading 4 zeros , where p is the previous p'
        - return: <int>
        """
        proof = 0
        last_proof = self.last_block['proof']
        while self.valid_proof(last_proof,proof)==False:
            proof+=1
        return proof

    def valid_proof(self,last_proof, proof):
        """
        Validates the Proof: Does hash(last_proof, proof) contain 5 leading zeroes?
        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :return: <bool> True if correct, False if not.
        """
        block_string = json.dumps(self.current_transactions,sort_keys=True)
        guess = f'{last_proof}{proof}{block_string}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:5] == "00000"

    # registrating current node to the ledger
    def register_node(self,address):
        """t
        Add a new node to the list of nodes

        :param address: <str> Address of node, Eg. 'http://192.168.0.5:5000'
        :return: None
        """
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    """
    will check prev element hash in current element field
    and will check if current hash has five leading zero with our proof of work
    """
    def valid_chain(self,chain):
        """"
        Determining if a given blockchain is valid

        :param chain: <list> A blockchain
        :return : <bool> True if valid , False if not
        """

        previous_block = self.chain[0]
        for i in range(1,len(self.chain)):
            block = self.chain[i]
            
            print(f'{previous_block}')
            print(f'{block}')
            print("\n-----------\n")

            if block['prev_hash'] != self.hash(previous_block):
                return False
            
            # Check that proof of work is correct
            if not self.valid_proof(previous_block['proof'],block['proof']):
                return False
            
            previous_block = block

        return True
    
    def resolve_conflicts(self):
        """
        This is the Consensus Algorithm , it resolved conflicts
        by replacing the chain with largest one in the network

        This method which loops through all our neighbouring nodes,
        downloads their chains and verifies them using the above method. 
        If a valid chain is found, whose length is greater than ours, 
        we replace ours.
        
        :return : <bool> True if our chain was replaced , False if not
        """
        neighbors = self.nodes
        new_chain = None

        # we are looking for chain longer then the current chain
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in the network
        for node in neighbors:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # check if the length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True
        
        return False
