from flask import Flask, request, jsonify
app = Flask(__name__)

shards = {}

# Testing shard
@app.route('/')
def init():
    shards["testuser"] = (4, 9)
    return 'Hello'
    
# Save shard (x, y) for that user
@app.route('/store', methods=['POST'])
def store_shard():
    # Get all url parameters
    username = request.args.get('username')
    x = request.args.get('x', type=int) 
    y = request.args.get('y', type=int)
    
    # Missing parameters
    if username is None or x is None or y is None:
        return jsonify({"error": "Missing parameters"}), 400

    # Store shard successfully
    shards[username] = (x, y)
    return jsonify({"status": "success", "message": f"Stored shard for {username}"})

# Retrieve the shard for that user
@app.route('/retrieve/<username>', methods=['GET'])
def retrieve_shard(username):
    # Get stored shard
    shard_tuple = shards.get(username)
    
    # User does not exist
    if shard_tuple is None:
        return jsonify({"error": "User is not found"}), 404
    
    # Found shard
    return jsonify({"shard": shard_tuple})

# Run locally to test
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000)