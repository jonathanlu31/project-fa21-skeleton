import random

def f(n):
    print(n)
    rand = random.seed(574839742)
    for i in range(1, n+1):
        t = random.randrange(1, 1441)
        d = random.randrange(1, 61)
        p = round(random.uniform(1.0, 100.0), 3)
        print(i, t, d, p)