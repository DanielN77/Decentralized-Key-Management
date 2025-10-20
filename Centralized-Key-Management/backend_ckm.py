import base64
import os
from flask import Flask, request, render_template
import json
from argon2.low_level import hash_secret_raw, Type
from flask_cors import CORS

# Init
app = Flask(__name__)
CORS(app)

# Help function that Gets users and their hashes
def load_users():
    with open("central_storage.json", "r") as f:
        return json.load(f)

@app.route('/login', methods = ['POST'])
def login():
    print("Hello")
    data = request.get_json()
    username = data.get("username", "")
    password = data.get("password", "")

    try:
        salt = get_salt(username)
        hash = hash_password(password, salt)
        
        users = load_users()

        if username not in users:
              return {"message": f"User '{username}' not found."}, 404
        
        stored_hash = base64.b64decode(users[username]["hash"].encode("utf-8"))
        
        if stored_hash == hash: # Correct password
            return  {"message": f"Welcome {username}"}
        else: # Incorrect password
            return {"message": "Wrong username or password."}
    except Exception as e:
        return {"message": f"Login failed due to error {str(e)}"}

@app.route('/register', methods=['POST'])
def register():
    print("Test")
    # Extract parameters
    data = request.get_json()
    username = data.get("username", "")
    password = data.get("password", "")
    users = load_users()

    # Both paramters are neeed
    if not username or not password:
        return {"message": "Username and password are both required."}
    if username in users:
        return {"message": f"User '{username}' already exists."}, 404
    
    try:
        salt = generate_salt(username)
        hash = hash_password(password, salt)
        users[username] = {
            "hash": base64.b64encode(hash).decode("utf-8")
        }
        with open("central_storage.json", "w") as f:
            json.dump(users, f, indent=2)
        return {"message": f"User '{username}' has successfully registered."}
    except Exception as e:
        return {"message": f"Registration failed due to {str(e)}"}

def generate_salt(username):

    salt = os.urandom(16)
    salt_enc = base64.b64encode(salt).decode("utf-8")
    record = { "username": username, "salt": salt_enc}

    # Save salt under associated username
    with open("central_salts.json", "a") as f:
        f.write(json.dumps(record) + "\n")
    
    return salt

def get_salt(username):
    salt_enc = None 
    
    with open("central_salts.json", "r") as f:
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)