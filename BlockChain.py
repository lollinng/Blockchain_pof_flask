import hashlib
import datetime as date
import json

class BlockChain():

    def __init__(self):
        self.chain = []
        self.chain.append({
            "index": len(self.chain)+1,
            "timestamp":str(date.datetime.now()), 
            "data" : "1st block",
            "proof" : 1,
            "prev_hash" : '0'
        })

    def create_block(self,proof,data):
        previous_hash = self.hash(self.print_previous_block())
        block = {
            "index": len(self.chain)+1,
            "timestamp":str(date.datetime.now()), 
            "data" : data,
            "proof" : proof,
            "prev_hash" : previous_hash
        }
        self.chain.append(block)
        return block
    
    def print_previous_block(self):
        return self.chain[-1]
    
    # pow if used to mine the block
    def proof_of_work(self):
        new_proof = 1
        prev_proof = self.print_previous_block()['proof']
        check_proof = False

        while check_proof is False:
            hash_operation = hashlib.sha256(
                str(new_proof**2 - prev_proof**2).encode()
            ).hexdigest()
            
            if hash_operation[:5] == "00000":
                check_proof = True
            else:
                new_proof+=1
        return new_proof
    
    def hash(self,block):
        encoded_block_string = json.dumps(block,sort_keys=True).encode()
        return hashlib.sha256(encoded_block_string).hexdigest()
    

    """
    will check prev element hash in current element field
    and will check if current hash has five leading zero with our proof of work
    """
    def chain_valid(self):
        previous_block = self.chain[0]
        for i in range(1,len(self.chain)):
            block = self.chain[i]
            if block['prev_hash'] != self.hash(previous_block):
                return False
            
            prev_proof = previous_block['proof']
            new_proof = block['proof'] 
            hash_operation = hashlib.sha256(
                str(new_proof**2 - prev_proof**2).encode()
            ).hexdigest()
            if hash_operation[:5] != "00000":
                return False
            
            previous_block = block

        return True
    
