def modular_inverse(a:int, m:int)->int:    
    start_m = m
    u_0 = 1
    u_1 = 0
    
    while a>1:
        q = a // m
        a, m = m, a % m
        u_0, u_1 = u_1, u_0 - q * u_1

    if (u_0 < 0):
        u_0 += start_m

    return u_0

def gcd(a: int,b: int) -> int:
    while b:
        a, b = b, a % b
    return a

def mod_pow_horner(a: int, m: int, n: int) -> int:
    b = 1
    bin_m = bin(m)[2:]

    for bit in bin_m:
        b = (b * b) % n
        if bit == '1':
            b = (b * a) % n
    return b