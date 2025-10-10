import numpy as np

def deconstruct(pwd, n, t):  # pwd is assumed to be sent as bytes
    s = int.from_bytes(pwd, byteorder="big")  # Convert bytes to an integer

    p = 2**256 + 297 # Prime guaranteed larger than s since pwd is 32 bytes (256 bits) fixed length for Argon2id
    coef = [np.random.randint(low=1, high=p) for _ in range(t-1)]

    # Polynomial
    f = construct_poly(coef, s, p)

    # Evaluation
    shards = set()

    for x in range(1, n+1):
        y = f(x)
        shards.add((x, y))

    return shards  # Set with n shards


# https://medium.com/@compuxela/horners-method-for-polynomial-evaluation-a13dbf9749a2
def construct_poly(coef, s, p):

    coef = coef + [s]  # Adds s as last coefficient

    # Function f(x) with Horner's method
    def f(x):  
        r = coef[0]  # The x^n coeffiecient

        for i in range(1, len(coef)):
            r = (r*x + coef[i]) % p
        return r
    
    return f

