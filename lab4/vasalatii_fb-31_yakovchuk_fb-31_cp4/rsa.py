from dataclasses import dataclass
from modular_arithemtic import modular_inverse, mod_pow_horner
from primes_gen import generate_strong_prime

@dataclass
class KeyPair:
    pub_key: tuple[int,int]
    priv_key: tuple[int,int,int]

e = 2**16+1

def _gen_key_pair(p:int, q:int, e:int) -> KeyPair:
    n = p * q
    phi_n = (p-1) * (q-1)
    d = modular_inverse(e, phi_n)
    return KeyPair(pub_key=(e, n), priv_key=(d, p, q))

def gen_key_pair(bits:int) -> KeyPair:
    if bits < 256:
        raise ValueError("please enter key length equal or bigger than 256") 
    p = generate_strong_prime(bits=bits//2)
    q = generate_strong_prime(bits=bits//2)
    return _gen_key_pair(p, q, e)

def encrypt(pt:int, e:int, n:int) -> int:
    if pt >= n:
        raise ValueError("Message is larger than modulus")
    return mod_pow_horner(pt, e, n)

def decrypt(ct:int, d:int, n:int) -> int:
    return mod_pow_horner(ct, d, n)

def sign(pt:int, d:int, n:int) -> tuple[int,int]:
    return pt, mod_pow_horner(pt, d, n)

def verify(pt:int, s:int, e:int, n:int) -> bool:
    return pt == mod_pow_horner(s, e, n)

def prep_key_for_sending(k:int, send_d:int, send_n:int, recv_exp:int, recv_n:int) -> tuple[int,int]:
    if send_n > recv_n:
        raise ValueError("Reciever modulus should be equal or bigger to sender modulus")
    _, s = sign(k, send_d, send_n)
    return encrypt(k, recv_exp, recv_n), encrypt(s, recv_exp, recv_n)

def retrieve_key(k_recv:int, s_recv:int, recv_d:int, recv_n:int, send_e:int, send_n:int) -> tuple[int,int,bool]:
    k = decrypt(k_recv, recv_d, recv_n)
    s = decrypt(s_recv, recv_d, recv_n)
    return k, s, verify(k, s, send_e, send_n)