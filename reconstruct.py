import numpy as np

def reconstruct(shards):  # Set with shards (x, f(x))
    p = 2**256 + 297

    nodes = [x for x, _ in shards]  
    vals  = [y for _, y in shards]


    # Lagrange polynomial
    def L(x):
        full = 0
        for j in range(len(nodes)):
            l_j = construct_lagrange(nodes[j], nodes, p, j)

            full = (full + vals[j] * l_j(x)) % p
        return full
    

    s = L(0) % p

    pwd = s.to_bytes(32, byteorder="big")
    return pwd  # Returned as bytes

def construct_lagrange(x_j, nodes, p, j):

    # Horner's method
    def l_j(x):  
        product = 1 

        for m in range(len(nodes)):
            x_m = nodes[m]

            if m == j:
                continue

            nom = (x-x_m) % p
            denom = (x_j - x_m) % p
            product = (product * nom * pow(denom, -1, p)) % p  # Modular inverse mod p insteaad of division

        return product
    
    return l_j

