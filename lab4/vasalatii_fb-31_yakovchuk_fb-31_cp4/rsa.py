from dataclasses import dataclass
from modular_arithemtic import modular_inverse, mod_pow_horner

@dataclass
class KeyPair:
    pub_key: tuple[int,int]
    priv_key: tuple[int,int,int]

e = 2**16+1

def gen_key_pair(p:int,q:int,e:int) -> KeyPair:
    n = p * q
    phi_n = (p-1) * (q-1)
    d = modular_inverse(e, phi_n)
    return KeyPair(pub_key=(e,n),priv_key=(d, p, q))

def encrypt(pt:int,e:int,n:int) -> int:
    return mod_pow_horner(pt,e,n)

def decrypt(ct:int,d:int, n:int) -> int:
    return mod_pow_horner(ct, d, n)

def sign(pt:int,d:int, n:int) -> tuple[int,int]:
    return (pt, mod_pow_horner(pt,d,n))

def verify(pt:int,s:int,e:int,n:int) -> bool:
    return pt == mod_pow_horner(s,e,n)

def prep_key_for_sending(k:int,send_d:int, send_n:int, recv_exp:int,recv_n:int) -> tuple[int,int]:
    s = mod_pow_horner(k,send_d,send_n)
    return (mod_pow_horner(k,recv_exp,recv_n),mod_pow_horner(s,recv_exp,recv_n))

def retrieve_key(k_recv:int, s_recv:int, recv_d:int, recv_n:int, send_e:int,send_n:int) -> tuple[int,int,bool]:
    k = mod_pow_horner(k_recv,recv_d,recv_n)
    s = mod_pow_horner(s_recv,recv_d,recv_n)
    return (k,s,verify(k,s,send_e,send_n))