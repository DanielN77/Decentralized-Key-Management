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

# Initialize global variables
NUM_NODES=5
THRESHOLD=3

# Initialize file storage
node_dir = os.path.join("..", "nodes")
os.makedirs(node_dir, exist_ok=True)
salt_path = os.path.join("..", "salts.json")

@app.route('/login', methods = ['POST'])
def login():
    """Handles login by checking the input password is correct i.e. same as reconstructed password.

    Returns:
        dict: A dictionar containing a status message.
    """
    
    data = request.get_json()
    username = data.get("username", "")
    password = data.get("password", "")
    
    print(f"Username:{username}")
    print(f"Password: {password}")
    
    try:
        # Reconstruct hashed password
        shards = get_Shards(username, THRESHOLD)
        reconstructed_pass = reconstruct(shards)
        
        # Hash the input password
        salt = get_salt(username)
        hashed_pwd = hash_password(password, salt)
        
        # Debug the passwords
        print(f'Reconstructed password: {reconstructed_pass}')
        print(f'Hashed input password: {hashed_pwd}')
        
        # Correct password
        if username and hashed_pwd == reconstructed_pass:
            message = "Welcome " + username
            return  {"message": message}
        else:
            message = "Wrong username or password."
            return {"message": message}
    except Exception as e:
        return {"message": f"Login failed due to error {str(e)}"}

@app.route('/register', methods=['POST'])
def register():
    """Handles registration by storing the password shards across nodes.

    Returns:
       dict: A dictionary containing status message.
    """
    
    # Extract paramters
    data = request.get_json()
    username = data.get("username", "")
    password = data.get("password", "")

    # Both paramters are neeed
    if not username or not password:
        return {"message": "Username and password are both required."}
    
    # Store the shards accross the nodes
    try:
        store_shards(username, password, NUM_NODES, THRESHOLD)
        return {"message": f"User '{username}' has successfully registered."}
    except Exception as e:
        return {"message": f"Registration failed due to {str(e)}"}

def store_shards(username, password, n, t):
    """Deconstruct password and store the resulting shards in node_i.json files.

    Args:
        username (str): The username that will be stored with each shard.
        password (str): The password that is being deconstructed.
        n (int): The number of nodes to create.
        t (int): The threshold for reconstruction.
    """
    
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

def get_Shards(user, t):
    """Retrieve the shards for the given user.

    Args:
        user (str): The username for which the shards are retrieved for.
        t (int): The threshold of the number of nodes needed for reconstruction.

    Raises:
        ValueError: If too many nodes are unavailable.
        ValueError: If no shards are found.

    Returns:
        List[Tuple[int, int]]: A list of shards.
    """
    
    shards = []
    num_nodes = 0

    # Search shards in each node file
    for node in os.listdir(node_dir):

        # Read file
        with open(os.path.join(node_dir, node), "r") as f:
            
            for line in f:
                try:
                    # Load the json record
                    record = json.loads(line)
                    print(f'Check record: {record}')
                    
                    # Same user then capture the shard
                    if record.get("username") == user:
                        print(f"Found the shard for the user {user}")
                        shards.append(tuple(record["shard"]))
                except:
                    continue
            
            num_nodes += 1
    
    
    # Too many nodes are unavailable e.g. due to DOS
    if num_nodes < t:
        raise ValueError("Too few nodes currently available in storage to reconstruct shards.")
    
    # No record of user exists i.e. no shards found
    if len(shards) == 0:
        raise ValueError("User does not exist in storage.")
                
    print(f'The shards for the user {user}: {shards}')
    return shards

def hash_password(password, salt):
    """Hash the given password with the specified salt.

    Args:
        password (str): The password being hashed.
        salt (bytes): The salt used in the hashing.

    Returns:
        bytes: The hashed salted password in bytes.
    """
    
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
    """Generate a random salt and store it in salts.json file.

    Args:
        username (str): The username whose salt is being generated.

    Returns:
        bytes: The salt in bytes.
    """

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
    """Retrieve a user's salt from the salts.json file.

    Args:
        username (str): The username whose salt is being retrieved.

    Raises:
        ValueError: If no salt is found for the specified user.

    Returns:
        bytes: The salt in bytes.
    """
    
    salt_enc = None 
    
    with open(salt_path, "r") as f:
        for line in f:
            try:
                # Get the salt record
                record = json.loads(line)
                print(f'Check record: {record}')
                
                # Same user then capture the salt
                if record.get("username") == username:
                    print(f"Found the salt for the user {username}")
                    salt_enc = record["salt"]
            except:
                continue
                 
    if not salt_enc:
        raise ValueError(f"Missing salt for user '{username}'")

    # Decode the encoding for json storage
    return base64.b64decode(salt_enc.encode("utf-8"))
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)