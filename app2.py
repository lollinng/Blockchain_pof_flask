from flask import Flask,jsonify, request
from uuid import uuid4
from BlockChain import BlockChain


app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-','')

blockchain = BlockChain()

@app.route('/transactions/new',methods=['POST'])
def new_transaction():

    values = request.get_json()

    # check if the required fields are in the POSt'ed data
    # required = ['sender', 'recipient', 'amount']
    # if not all(k in values for k in required):
    #     return 'Missing values', 400
    
    # create a new transaction
    index =  blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201

@app.route('/mine',methods=['GET'])
def mine_block():

    # running proof of work algorithm to get the next proof.
    poof = blockchain.proof_of_work()

    # We must receive a reward for finding the proof.
    # The sender is "0" to signify that this node has mined a new coin.
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1
    )

    # Forge the new Block by adding it to the chain
    prev_hash = blockchain.hash(blockchain.last_block)

    block = blockchain.create_block(prev_hash,poof)

    response = {'message': 'A block is MINED',
                'index': block['index'],
                'transactions':block['transactions'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash':block['prev_hash']
                }
    return jsonify(response), 200

@app.route('/get_chain',methods=['GET'])
def display_chain():
    response = {
        "chain" : blockchain.chain,
        'length' : len(blockchain.chain)
    }
    return jsonify(response),200

@app.route('/valid',methods=['GET'])
def valid():
    valid = blockchain.valid_chain()
    if valid:
        response = {'message': 'The Blockchain is valid.'}
    else:
        response = {'message': 'The Blockchain is not valid.'}
    return jsonify(response), 200

@app.route('/nodes/register',methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes",400
    
    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message':'New nodes have been added',
        'total_nodes': list(blockchain.nodes)
    }
    return jsonify(response),201

@app.route('/nodes/resolve',methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message':'Our chain was replaced',
            'chain':blockchain.chain
        }
    else:
        response = {
            'message':'Our chain is authoritative',
            'chain':blockchain.chain
        }

    return jsonify(response), 200

app.run(host='127.0.0.1',port=5001)