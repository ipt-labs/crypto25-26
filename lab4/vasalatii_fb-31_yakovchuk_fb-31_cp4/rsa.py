from dataclasses import dataclass
from modular_arithemtic import modular_inverse, mod_pow_horner

@dataclass
class KeyPair:
    pub_key: tuple[int,int]
    priv_key: tuple[int,int,int]

e = 2**16+1

def gen_key_pair(p:int,q:int) -> KeyPair:
    n = p * q
    phi_n = (p-1) * (q-1)
    d = modular_inverse(e, phi_n)
    return KeyPair(pub_key=(n,e),priv_key=(p,q,d))

def encrypt(pt:int,e:int,n:int) -> int:
    return mod_pow_horner(pt,e,n)

def decrypt(ct:int,d:int, n:int) -> int:
    return mod_pow_horner(ct, d, n)