import os
from flask import Flask, request, render_template
import json
from deconstruct import deconstruct
from reconstruct import reconstruct
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Initialize global vars
shards = {}
node_dir = os.path.join("..", "nodes")
os.makedirs(node_dir, exist_ok=True)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        shards = get_Shards(username)
        reconstructed_pass = reconstruct(shards)

        if username and password == reconstructed_pass:
            message = "Welcome " + username
            return  {"message": message}
        else:
            message = "Wrong username or password."
            return {"message": message}
    
    else: # Om det är GET så går vi till login formuläret och visar den
        return render_template("login.html")


def get_Shards(user):
    shards = []

    # Search shards in each node file
    for node in os.listdir(node_dir):

        # Read file
        with open(os.path.join(node_dir, node), "r") as f:
            for line in f:
                try:
                    # Load the json record
                    record = json.loads(line)
                    
                    # Same user then capture the shard
                    if record.get("username") == user:
                        shards.append(tuple(record["shard"]))
                except:
                    continue
    print(shards)
    
    return shards


@app.route('/register', methods=['POST'])
def register():
    
    # Extract paramters
    data = request.get_json()
    username = data.get("username", "")
    password = data.get("password", "")

    # Both paramters are neeed
    if not username or not password:
        return {"message": "Username and password are both required."}
    
    try:
        store_shards(username, password)
        return {"message": f"User '{username}' has successfully registered."}
    except Exception as e:
        return {"message": f"Registration failed because of {str(e)}"}


def store_shards(username, password, n=5, t=3):
    
    # Ensure password is 32 bytes
    pwd_b = password.encode("utf-8").ljust(32, b'\0')[:32]
    print(pwd_b)
    
    # Deconstruct the password
    shards = list(deconstruct(pwd_b, n, t))
    
    # Dummy shards
    # shards = [
    #     (1, 842394),
    #     (2, 1293847),
    #     (3, 1938475),
    #     (4, 2493847),
    #     (5, 3129384)
    # ]

    # Save the shard for each node
    for i in range(n):
        
        # The username and the ith shard
        x, y = shards[i]
        record = {"username": username, "shard": [x, y]}
        
        # Append shard to node via json
        with open(f"nodes/node_{i+1}.json", "a") as f:
            f.write(json.dumps(record) + "\n")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)