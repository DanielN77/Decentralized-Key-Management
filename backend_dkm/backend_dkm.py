import base64
import os
from flask import Flask, request, render_template
import json
from deconstruct import deconstruct
from reconstruct import reconstruct
from argon2.low_level import hash_secret_raw, Type
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Initialize global vars
shards = {}
node_dir = os.path.join("..", "nodes")
os.makedirs(node_dir, exist_ok=True)
salt_path = os.path.join("..", "salts.json")

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get("username", "")
        password = data.get("password", "")
        
        print(f"Username:{username}")
        print(f"Password: {password}")
        
        # Reconstruct hashed password
        shards = get_Shards(username)
        reconstructed_pass = reconstruct(shards)
        print(f'Reconstructed password: {reconstructed_pass}')
        
        # pwd_b = password.encode("utf-8").ljust(32, b'\0')[:32]
        
        # Hash the input password
        salt = get_salt(username)
        hashed_pwd = hash_password(password, salt)
        
        # Correct password
        if username and hashed_pwd == reconstructed_pass:
            message = "Welcome " + username
            return  {"message": message}
        else:
            message = "Wrong username or password."
            return {"message": message}
    
    # else: # Om det är GET så går vi till login formuläret och visar den
    #     return render_template("login.html")

@app.route('/register', methods=['POST'])
def register():
    
    # Extract paramters
    data = request.get_json()
    username = data.get("username", "")
    password = data.get("password", "")

    # Both paramters are neeed
    if not username or not password:
        return {"message": "Username and password are both required."}
    
    # Store the shards accross the nodes
    try:
        store_shards(username, password)
        return {"message": f"User '{username}' has successfully registered."}
    except Exception as e:
        return {"message": f"Registration failed because of {str(e)}"}


def store_shards(username, password, n=5, t=3):

    # pwd_b = password.encode("utf-8").ljust(32, b'\0')[:32]
    # print(f'Password in bytes: {pwd_b}')
    
    # Ensure password is hashed and 32 bytes
    salt = generate_salt(username)
    hashed_pwd = hash_password(password, salt)
    print(f'Hashed password in bytes: {hashed_pwd}')
    
    # Deconstruct the password
    shards = list(deconstruct(hashed_pwd, n, t))

    # Save the shard for each node
    for i in range(n):
        
        # The username and the ith shard
        x, y = shards[i]
        record = {"username": username, "shard": [x, y]}
        
        # Append shard to node via json
        with open(node_dir+f"/node_{i+1}.json", "a") as f:
            f.write(json.dumps(record) + "\n")

def get_Shards(user):
    shards = []

    # Search shards in each node file
    for node in os.listdir(node_dir):

        # Read file
        with open(os.path.join(node_dir, node), "r") as f:
            for line in f:
                
                # Load the json record
                record = json.loads(line)
                print(f'Check record: {record}')
                
                # Same user then capture the shard
                if record.get("username") == user:
                    print(f"Found the shard for the user {user}")
                    shards.append(tuple(record["shard"]))
                
    print(f'The shards for the user {user}: {shards}')
    return shards

def hash_password(password, salt):
    hashed_bytes = hash_secret_raw(
        secret=password.encode("utf-8"),
        salt=salt,
        time_cost=3,
        memory_cost=65536,
        parallelism=1,
        hash_len=32,
        type=Type.ID
    )
    return hashed_bytes

def generate_salt(username):

    # Generate salt
    salt = os.urandom(16)
    
    # Encode to base64 for json storage
    salt_enc = base64.b64encode(salt).decode("utf-8")

    # Generate salt record
    record = { "username": username, "salt": salt_enc}

    # Save salt after username
    with open(salt_path, "a") as f:
        f.write(json.dumps(record) + "\n")
    
    return salt

def get_salt(username):

    with open(salt_path, "r") as f:
        for line in f:
                
            # Get the salt record
            record = json.loads(line)
            print(f'Check record: {record}')
            
            # Same user then capture the salt
            if record.get("username") == username:
                print(f"Found the salt for the user {username}")
                salt_enc = record["salt"]
                 
        if not salt_enc:
            raise ValueError(f"Missing salt for user '{username}'")

        # Decode the encoding for json storage
        return base64.b64decode(salt_enc.encode("utf-8"))
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)