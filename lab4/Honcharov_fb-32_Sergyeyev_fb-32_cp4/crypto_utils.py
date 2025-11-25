import random
import hashlib
import sys

sys.setrecursionlimit(2000)

FIRST_PRIMES = [
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 
    71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 
    149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 
    227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 
    307, 311, 313, 317, 331, 337, 347, 349
]

def modular_exponentiation(x, a, m):
    binary_a = bin(a)[2:]
    k = len(binary_a)
    y = 1
    for i in range(k):
        y = (y * y) % m 
        if binary_a[i] == '1':
            y = (y * x) % m 
    return y

def extended_euclidean_algorithm(a, b):
    if b == 0:
        return 1, 0, a
    else:
        x, y, gcd = extended_euclidean_algorithm(b, a % b)
        return y, x - (a // b) * y, gcd

def modular_inverse(e, m):
    x, y, gcd = extended_euclidean_algorithm(e, m)
    if gcd != 1:
        raise ValueError("Обернений елемент не існує")
    else:
        return x % m

def trial_division(n, prime_list):
    for p in prime_list:
        if p * p > n:
            break
        if n % p == 0:
            return False
    return True

def generate_random_odd_number(bit_length):
    n = random.getrandbits(bit_length)
    n |= (1 << (bit_length - 1))
    n |= 1
    return n

def miller_rabin_test(p, k):
    s = 0
    d = p - 1
    while d % 2 == 0:
        d //= 2
        s += 1
        
    for _ in range(k):
        x = random.randint(2, p - 2) 
        x_d = modular_exponentiation(x, d, p)
        
        if x_d == 1 or x_d == p - 1:
            continue
            
        is_pseudo_prime = False
        for r in range(1, s):
            x_r = modular_exponentiation(x_d, 2, p)
            x_d = x_r
            if x_r == p - 1:
                is_pseudo_prime = True
                break
            if x_r == 1:
                return False
        
        if not is_pseudo_prime:
            return False
            
    return True

def find_prime(bit_length):
    while True:
        n = generate_random_odd_number(bit_length)
        if not trial_division(n, FIRST_PRIMES):
            continue
        if miller_rabin_test(n, k=10):
            return n
        else:
            print(f"Число {n} не пройшло тест Міллера-Рабіна")

def hash_function(message):
    if isinstance(message, str):
        message_bytes = message.encode('utf-8')
    else:
        message_bytes = message
    
    hash_bytes = hashlib.sha256(message_bytes).digest()
    hash_int = int.from_bytes(hash_bytes, 'big')
    return hash_int