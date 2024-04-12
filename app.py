from flask import Flask,jsonify

from BlockChain import BlockChain


app = Flask(__name__)

blockchain = BlockChain()

@app.route('/mine_block/<data>',methods=['GET'])
def mine_block(data):
    poof = blockchain.proof_of_work()
    block = blockchain.create_block(poof,data)
    response = {'message': 'A block is MINED',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'data' :data,
                'proof': block['proof'],
                }
    return jsonify(response), 200

@app.route('/get_chain',methods=['GET'])
def display_chain():
    response = {
        "chain" : blockchain.chain,
        'length' : len(blockchain.chain)
    }
    return jsonify(response),2000

@app.route('/valid',methods=['GET'])
def valid():
    valid = blockchain.chain_valid()
    if valid:
        response = {'message': 'The Blockchain is valid.'}
    else:
        response = {'message': 'The Blockchain is not valid.'}
    return jsonify(response), 200


app.run(host='127.0.0.1',port=5000)