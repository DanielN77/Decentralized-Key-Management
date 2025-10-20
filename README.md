# Cybersecurity Project Report
Sofia Fasth Gillstedt, Marina Apelgren, Daniel Norman, Tenzin Sangpo Choedon
October 2025

# 1. Problem statement

In today’s society, where cyber attacks and online identity theft are prevalent, it is important to
implement good defenses that do not allow data leakage. In the case of websites, it is especially
important to protect the integrity of the users by safely storing their passwords. But how can one
safely do so?
The easiest and less costly way to store different passwords is by using a centralized database,
where the usernames and passwords are stored together in the same place. This set-up is very
vulnerable to attacks and leakage since one successful attack allows the hacker to have access to
the passwords of every user. Granted, the passwords are hashed and perhaps salted, but this does
not guarantee safety since this method is not IND-CPA secure and is deterministic.
Using a centralized database causes one to become susceptible to denial of service (DoS) attacks
since a centralized database creates a single bottleneck. If an attacker floods the victim’s network,
the overwhelmed resources deny service to legitimate users.
We notice that the reward for a single successful attack is therefore very unproportional.
To mitigate these risks, one can use a decentralized database instead, where each password
is split into shards and stored separately in different databases. This prevents the attacker from
knowing the whole password after one attack. Instead, the attacker will only get a piece of the password and will need many more to decode the whole password. One method, utilizing decentralized
databases, is Shamir Secret Sharing (SSS), which allows us store each password in smaller shards.
Leaking a certain number of shards (less than a threshold) will not affect the reconstruction of the
password. This is also the method we have decided to implement and explore further.

# 2. Project idea

We want to test the security and limitations of SSS. To do this, we started by developing a demo
website with authentication. When someone registers, we store the password in a decentralized
key management system that we have implemented. When someone tries to log in, we fetch the
password from the different shards of the decentralized system to reconstruct the password and
compare it to the one the user tried to log in with. We will then simulate a number of attacks
and compare the result with the centralized key management system to show to what extent a
decentralized system is better.

# 3. Documentation of project

## 3.1 What is SSS?

Shamir’s Secret Sharing (SSS) is a so called threshold-based cryptographic scheme used to distribute responsibility for password management among multiple parties. In our implementation
we will call these parties nodes.
The idea is that information about the secret is divided into n number of shares which are then
stored on one node each. Only when a predefined minimum number of shares, t, are combined can
the original secret be reconstructed. Fewer than t shares will not reveal any information about
the secret.

The method is based heavily on mathematics and interpolation as described below.
1. Decide on the desired number of shares, n, and the threshold, t.
2. Represent the secret, s, as an integer
3. Construct a polynomial, f(x), of degree t where s is the constant term and the coefficients
for x^i , i > 0 are randomized.
4. Store n shares as: (1, f (1)), (2, f (2)), ..., (n, f (n))
Now, these shares reveal no information about the secret value s unless you have ≥ t number of
shares and you do not store the secret anywhere. In the case that you do have access to at least t
shares you are able to use Lagrange interpolation in order to reconstruct the polynomial uniquely,
thus retrieving the constant term, our secret, s.

Some advantages of using SSS as a method for storing secrets should now be clear, mainly mitigating the risk of having a single point of failure which can lead to mass-leaks following a single
breach of security. Furthermore, by finding a good balance between the number of shares and the
threshold there are arguments to be made about mitigating risks of Denial of Service attacks as
well, since in theory as many as n − t nodes can be inaccessible while still maintaining access to
the secret.
However, as with any scheme there are disadvantages as well. In our case, the main problem
is the cost of implementing it on a large scale. For greater security we would wish to have a large
threshold which would require many nodes being stored and accessible. This comes with costs of
having multiple servers up and running which is costly.

## 3.2 Implementation

Our aim was to simulate a website where users register and login with a username and password.
Later on we want to test the difference in security between storing the secret using a centralized
vs decentralized approach.
Therefore, only the backend differs between the two approaches and the frontend stays the same.
The frontend was implemented using HTML- and CSS-code with an input field for username and
password.
For a first time user this will trigger a register-request to the backend which is implemented
with a flask-app. A random salt is added to the password which is then hashed using an Argon2id
hashing-algorithm with 32-byte length parameter. The secret hash is then stored differently for
the centralized and decentralized approach.

### 3.2.1 Decentralized

For the decentralized approach the hash needs to be deconstructed into shares according to
Shamir’s Secret Sharing scheme. In the register-request we call upon a function deconstruct.py.
Following the method described in section 3.1, but with additional prime-modular calculations for
added security, this function then deconstructs the secret into n shares.
The reason why using arithmetic modular calculation increases security is because we place all
operations in a proper finite field, where every non-zero element has an inverse and polynomial
interpolation is well defined. This is essential for SSS, where exactly t shards uniquely reconstruct
the secret, while any fewer provide no information (“perfect secrecy”), because many different polynomials, and thus secrets, fit the same partial shares. Working in a field also keeps share
values uniformly distributed and avoids practical leaks from integer/float quirks such as overflows,
carries, rounding, or non-invertible denominators.
The shards are then returned to the register function which stores each share on a separate
node. These nodes can be implemented in many ways such as files, databases, or as we chose,
dockerfiles.
When an already registered user then wishes to login he/she writes their username and password
in the login-field of the website which triggers a login-request instead.
The salt corresponding to the specific user is appended to the written password and hashed.
All that remains is to check if this is the same as the stored password-hash.
The login-request, therefore, retrieves the shares associated with the user from the nodes.
Using the shares on the form (x, f (x)) the function reconstruct.py is called. reconstruct.py
uses Lagrange interpolation to reconstruct the same polynomial, f , that was used in deconstruct
to produce the shares (x, f (x)). Once this polynomial is found we can easily retrieve the secret as
the constant term, s, convert it back to bytes and return it to the login-function.
Lastly, we only need to compare this correct password associated with the user to the hash of
the input from the login-page. If they are identical, the login-request is successful and otherwise
the request is denied.

### 3.2.2 Centralized

The register-request creates a new user and stores the username, salt and hashed password in
the central database together with possible other users.
In order to login a request is sent to retrieve the stored salt and hashed password associated with
the user. The input-password is hashed with the same salt and then compared to the stored hash.
If identical, login is successful and if not it is denied.

# 4 Documentation on testing the project

We implemented this method with certain threat model in mind and possible defenses to help us
analyze its risks. Foremost, we wanted to simulate DoS attacks and invasion of nodes. We felt that
these attacks best described the different possible attacks and allowed us to analyze the strength
and weaknesses of the decentralized databases and compare it to the centralized one.

## 4.1 Decentralized

### 4.1.1 DoS mitigation

**Threat models**
We chose to simulate two different DoS attacks, where the attacker destroys a number of nodes,
and we try to reconstruct the password if possible:
Threat model 1: We assume that the attacker compromises m nodes and the number of remaining nodes is above the threshold number t.
Threat model 2: We assume that the attacker compromises m nodes and the number of remaining nodes is under the threshold number t.

**Defenses**
We used SSS, meaning we only need t nodes to reconstruct the secret.
Implementation
To simulate these attacks, we assumed that we only have access to n − m nodes, where n is the
total number of nodes and m is the number of compromised nodes. For simulating this attack we
chose the total number of nodes n = 10, the threshold t = 4, meaning we need at least 4 nodes to
be able to reconstruct our password.
In the first case, our attacker has compromised m = 3 nodes we have l = n − m = 10 − 3 = 7 >
t = 4 functioning nodes left. We simulated the destruction of 3 nodes by selecting 7 nodes from the 10 available nodes. So, when we used our reconstruct function to reconstruct the password,
we sent in as parameter the randomly selected 7 nodes.
The result we got was the same as the theoretical one: we could reconstruct our password!
This was made possible because the number of remaining nodes was still above the set threshold.
In the second case, our attacker compromises m = 7 nodes. The number of remaining operating
nodes is now less than the set threshold, l = n − m = 10 − 7 = 3 < t = 4. We implemented this
attack in the same way as the first attack by randomly choosing 3 nodes from the total number
of nodes. We then tried, in the same way as before, to reconstruct the password with the chosen
3 nodes. As expected we could not recreate the password! The number of remaining functioning
nodes were not enough, which is also supported by the theoretical background.

### 4.1.2 Invasion of nodes mitigation (single point of failure)
We have explored the case where the attacker destroys the nodes, but what happens if the attacker
decides to read the content instead and leaves the node intact for us to still use? This is especially
dangerous since we do not know if the attacker has read a node or not or how many he has read.

**Threat models**
We assume that the attacker can only read a number m of nodes but does not compromise the
content. With this, we created three different threat models:
Threat model 1: The attacker can access and read m nodes where m is below the threshold t.
Threat model 2: The attacker can access and read m nodes where m is above or equal to the
threshold t.
Threat model 3: The attacker can access and read m nodes where m is above the threshold t
and the attacker has successfully decrypted the password.

**Defenses**
In the first case, our attacker does not have enough nodes to reconstruct the password, so we have
nothing to worry about and do not need to implement extra defenses.
In the second case, our attacker have sufficient nodes to reconstruct the password. Luckily, the
password is hashed and salted with Argon2 to add another step for the hacker since the attacker
now needs to brute force the decryption to get the unhashed password.
In the third case, we could use multi-factor authentication. Hence, even if the attacker was
successful in decrypting the password, they still will not be able to log into the account since they
still need another part for the full authentication. These other steps of authentication could be an
added passphrase or sending an authentication email.

**Implementation**
To implement these attack models, we store a password in n = 10 nodes and choose the threshold
as t = 4. The attacker can read m nodes, where m variates depending on the threat model.
To implement the attack model 1, we chose m = 3 < t = 4. We then send as parameter 3 nodes
to the reconstruct function but since m < t, the attacker could not reconstruct the password.
To implement the attack model 2, we choose m = 6 > t = 4. Same as for the attack model
1, we try to reconstruct the password with 6 nodes, and since m > t, the attacker was able to
reconstruct the password. But it remains hashed and salted, so the attacker still has to brute force
the decryption.
We could not implement the third threat model since it would take a lot more code and time
than we do not have. But in theory, this multi-factor authentication would significantly slow down
the attacker and it would take a lot more effort from the attacker to access the users account.

### 4.1.3 Discussion

We notice that as long as the attacker compromises or destroys m < t nodes we can still recreate
our password! And the attacker needs to read m ≥ t nodes to be able to reconstruct the password.
The question we now ask ourselves is: how do we choose the threshold and the total number of
nodes?

We want to choose a lower threshold to give us room to still be able to reconstruct the password
even if the attacker destroys a couple. But having a too low threshold makes it easier for the
attacker to read and reconstruct the password for himself.

## 4.2 Centralized

Since the centralized approach consists of only one node/database the threat model that we presume
is if the attacker either:
1. Gains access to reading the content of the database
2. Executes a Denial of Service attack, rendering the database unaccessible

1. We simulated this by acting as the attacker and then retrieving all stored passwords of the database.
Because of the salting and hash with Argon2id we will be slowed down trying to bruteforce the
passwords. However, for easily-guessed passwords we will eventually succeed.
2. In the case of a centralized approach a DoS-attack will prove fatal for accessiblity of the website.
Since the single database is critical in order to retrieve and store users/passwords noone will be
able to access their accounts. For this we do not have any defense if the DoS-attack succeeds.

# 5 Contributions

## 5.1 Tenzin Sangpo Choedon

1. Contributed partly to formulating initial project proposal and brainstorming the overall
architecture/layout of our project.
2. Implemented JSON storage for nodes and salts, including generating, storing and retrieval logic.
    - Implemented store shards() to save the deconstructed shards across nodes in JSON files.
    - Implemented get shards() to retrieve shards for the specified user from the nodes i.e. JSON files.
    - Implemented generate salt() to create a random value of 16 bytes and store it in salts.json file.
    - Implemented get salt() to retrieve user’s salt from the salts.json file.
3. Implemented most of backend logic for the decentralized version i.e. backend dkm.py
    - Implemented the handler register() to process user registration.
    - Modified the handler login() accordingly by adding functionality for retrieving salt,
    shards and hashing the input password.
    - Implemented exception handling and wrote comments in backend dkm.py for all functions.
    - Implemented hash password() to hash the password with the specified salt in bytes using argon2 module.
4. Performed initial tests for the decentralized version in the case of a DOS attack, based on threat model 1 and 2 described under DoS mitigation in the report. Simulating destoryed/unavailable nodes by deleting JSON node files. Then added exception handling if too few nodes are available to be able to reconstruct shards.

## 5.2 Sofia Fasth Gillstedt (in close collaboration with Marina)

1. Contributed partly to formulating initial project proposal and brainstorming the overall
architecture/layout of our project.
2. Completed research about SSS-scheme and desired functionality
    - In addition to learning SSS functionality we added modular calculations in order to
increase security. For this we also had to define a safe prime-field Zp by analytical
calculations from the assumption that the password is 32 bytes.
3. Implemented deconstruct.py
    - Used the secret-library in order to handle large integers and ran own tests to check input-functionality together with prime-field Zp
    - Used Horner’s method for constructing polynomials recursively
4. Implemented reconstruct.py
    - Lagrange-interpolation and ran own tests to check input-functionality together with prime-field Zp
5. Wrote the report for background on SSS, implementation etc.
6. Defined test-cases
    - Possible DoS scenarios, defined theoretical difference between centralized and decentralized approach.
    - Confidentiality scenarios and difference between centralized/decentralized
    - Discussed the thresholds and clarified that the implemented testing can be constructed in the same way for DoS/Confidentiality when looking at the decentralized apporach.
7. Took part in implementing backend logic for the login page (some parts ultimately not used because of changed approach)
    - BE login.py which was primed for flask/Docker implementation
## 5.3 Marina Apelgren (in close collaboration with Sofia)

1. Contributed partly to formulating initial project proposal and brainstorming the overall
architecture/layout of our project.
2. Completed research about SSS-scheme and desired functionality
    - In addition to learning SSS functionality we added modular calculations in order to
increase security. For this we also had to define a safe prime-field Zp by analytical
calculations from the assumption that the password is 32 bytes.
3. Implemented deconstruct.py
    - Used the secret-library in order to handle large integers and ran own tests to check input-functionality together with prime-field Zp
    - Used Horner’s method for constructing polynomials recursively
4. Implemented reconstruct.py
    - Lagrange-interpolation and ran own tests to check input-functionality together with
prime-field Zp
5. Wrote the report for background on SSS, implementation etc.
6. Defined test-cases
    - Possible DoS scenarios, defined theoretical difference between centralized and decentralized approach.
    - Confidentiality scenarios and difference between centralized/decentralized
    - Discussed the thresholds and clarified that the implemented testing can be constructed
in the same way for DoS/Confidentiality when looking at the decentralized apporach.
7. Took part in implementing backend logic for the login page (some parts ultimately not used because of changed approach)
    - BE login.py which was primed for flask/Docker implementation

## 5.4 Daniel Norman

1. Contributed partly to formulating initial project proposal and brainstorming the overall
architecture/layout of our project.
2. Implemented the front-end of the project (Found in the ’frontend’ folder)
    - Made the HTML page which calls the register() and login() functions in the backend.
    - Stylized the page for ease of use. Success/Error messages shown in order to display
what has happened in the backend
3. Implemented the back-end of the centralized key management system (Found in the ’CentralizedKey-Management’ folder)
    - Made generate salt(), get salt() and hash password() functions to work in the centralized version
    - Created a login() function that fetches the usernames hashed and salted password, and compares it to the salted and hashed input. Returns success/error messages to the front-end.
    - Created a register() function that stores a username and a salted hash in the central storage.json file. Stores all salts in their own central salts.json file. Returns success/error messages to the front-end.
4. Performed tests for a DoS attack on the centralized version and added exception handling
for such cases.
5. Made touch-ups on the report.

# References
[1] A. Shamir, “How to share a secret,” Communications of the ACM, 22(11), 1979.
Theoretical explanation of SSS and the properties of thresholds.
[2] A. Vassilev and L. Brandão, “NIST Kick-Starts ‘Threshold Cryptography’ Development Effort,” NIST News, 2020.
From NIST (National Institute of Standards and Technology) on the value of investing in
threshold based cryptographic scheme.
[3] OWASP, “Password Storage Cheat Sheet,” 2023. https://cheatsheetseries.owasp.org/
cheatsheets/Password_Storage_Cheat_Sheet.html
How to hash using the Argon2id-algorithm and explanation of its’ properties.
