import random

from crypto_utils import (
    modular_exponentiation, 
    modular_inverse, 
    find_prime, 
    hash_function,
    extended_euclidean_algorithm
)

def GenerateKeyPair(bit_length=256):
    p = find_prime(bit_length)
    q = find_prime(bit_length)
    n = p * q
    phi_n = (p - 1) * (q - 1) 

    #Випадкове е
    while True:
        e = random.randint(2, phi_n - 1)
        if e % 2 == 0:
            e += 1
        _, _, gcd = extended_euclidean_algorithm(e, phi_n)
        if gcd == 1:
            break 
        
    d = modular_inverse(e, phi_n) 
    
    public_key = (n, e)
    private_key = (d, p, q) 

    print(f"p = {p}")
    print(f"q = {q}")

    return public_key, private_key

def Encrypt(message, public_key):
    n, e = public_key
    ciphertext = modular_exponentiation(message, e, n)
    return ciphertext

def Decrypt(ciphertext, private_key):
    d, p, q = private_key
    n = p * q
    message = modular_exponentiation(ciphertext, d, n)
    return message

def Sign(message, private_key):
    d, p, q = private_key
    n = p * q
    hashed_message_int = int.from_bytes(message.encode('utf-8'), 'big')
    signature = modular_exponentiation(hashed_message_int, d, n)
    return signature

def Verify(message, signature, public_key):
    n, e = public_key
    decrypted_signature_int = modular_exponentiation(signature, e, n)
    hashed_message_int = int.from_bytes(message.encode('utf-8'), 'big') 
    return decrypted_signature_int == hashed_message_int

def SendKey(k, my_private_key, recipient_public_key):
    d, p, q = my_private_key
    n = p * q
    n1, e1 = recipient_public_key #
    
    S = modular_exponentiation(k, d, n)
    k1 = modular_exponentiation(k, e1, n1)
    S1 = modular_exponentiation(S, e1, n1) 
    
    return (k1, S1) 

def ReceiveKey(k1_S1_pair, my_private_key, sender_public_key):
    k1, S1 = k1_S1_pair
    d1, p1, q1 = my_private_key
    n1 = p1 * q1
    n, e = sender_public_key
    
    k = modular_exponentiation(k1, d1, n1)
    S = modular_exponentiation(S1, d1, n1)
    
    k_from_signature = modular_exponentiation(S, e, n)
    
    if k == k_from_signature: #
        return k, True
    else:
        return None, False