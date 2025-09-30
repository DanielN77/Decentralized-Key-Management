import numpy as np

def reconstruct(shards):
    p = 2**35 + 53

    nodes = [x for x, _ in shards]  
    vals  = [y for _, y in shards]


    # Lagrange polynomial
    def L(x):
        sum = 0
        for j in range(len(nodes)):
            l_j = construct_lagrange(nodes[j], nodes, p, j)

            sum += vals[j]*l_j(x)
        return sum
    

    s = L(0) % p
    return s

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
            product *= nom * pow(denom, -1, p)  # Modular inverse mod p insteaad of division
        return product
    
    return l_j


# Commands
s = reconstruct({(3, 22130049540), (2, 25036170937), (1, 6206241685), (4, 31847615915), (5, 19829131641)})
print(s)