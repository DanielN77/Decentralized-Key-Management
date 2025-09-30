import numpy as np

def deconstruct(s, n, t):
    p = 2**35 + 53
    coef = [np.random.randint(low=1, high=p) for _ in range(t-1)]

    # Polynomial
    f = construct_poly(coef, s, p)

    # Evaluation
    shards = set()

    for x in range(1, n+1):
        y = f(x)
        shards.add((x, y))

    return shards


# https://medium.com/@compuxela/horners-method-for-polynomial-evaluation-a13dbf9749a2
def construct_poly(coef, s, p):

    coef.append(s)  # Adds s as last coefficient

    # Function f(x) with Horner's method
    def f(x):  
        r = coef[0]  # The x^n coeffiecient

        for i in range(1, len(coef)):
            r = (r*x + coef[i]) % p
        return r
    
    return f


nodes = deconstruct(205, 5, 3)
print(nodes)