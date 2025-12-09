import secrets
import math
from typing import Tuple, Optional, List

def egcd(a: int, b: int) -> Tuple[int, int, int]:
    if b == 0:
        return a, 1, 0
    g, x1, y1 = egcd(b, a % b)
    return g, y1, x1 - (a // b) * y1


def mod_inverse(a: int, m: int) -> Optional[int]:
    g, x, _ = egcd(a, m)
    return None if g != 1 else x % m

def miller_rabin(n: int, rounds: int = 8) -> bool:
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False

    d = n - 1
    r = 0
    while d % 2 == 0:
        d //= 2
        r += 1

    for _ in range(rounds):
        a = secrets.randbelow(n - 3) + 2
        x = pow(a, d, n)

        if x in (1, n - 1):
            continue

        composite = True
        for _ in range(r - 1):
            x = pow(x, 2, n)

            if x == n - 1:
                composite = False
                break
            if x == 1:
                return False

        if composite:
            return False

    return True


def random_prime(bits: int, rounds: int = 8, track_fails: int = 30) -> int:
    if bits < 2:
        raise ValueError("bits must be >= 2")

    fails: List[int] = []

    while True:
        candidate = secrets.randbits(bits) | (1 << (bits - 1)) | 1

        if miller_rabin(candidate, rounds):
            if fails:
                print(
                    f"Failed candidates (last {len(fails[-track_fails:])}): "
                    f"{fails[-track_fails:]} (total {len(fails)})"
                )
            return candidate
        else:
            fails.append(candidate)

def make_keypair(bits: int = 256) -> Tuple[Tuple[int, int], Tuple[int, int, int]]:
    p = random_prime(bits)
    q = random_prime(bits)
    while q == p:
        q = random_prime(bits)

    n = p * q
    phi = (p - 1) * (q - 1)

    e = 65537
    if math.gcd(e, phi) != 1:
        while True:
            e = secrets.randbelow(phi - 2) + 2
            if math.gcd(e, phi) == 1:
                break

    d = mod_inverse(e, phi)
    if d is None:
        raise RuntimeError("Failed to compute modular inverse")

    return (n, e), (d, p, q)

def rsa_encrypt(m: int, e: int, n: int) -> int:
    return pow(m, e, n)

def rsa_decrypt(c: int, d: int, n: int) -> int:
    return pow(c, d, n)

def rsa_sign(m: int, d: int, n: int) -> int:
    return pow(m, d, n)

def rsa_verify(m: int, s: int, e: int, n: int) -> bool:
    return m == pow(s, e, n)

def send_key(msg: int, pub_sender, sec_sender, pub_receiver):
    n_s, e_s = pub_sender
    d_s = sec_sender[0]
    n_r, e_r = pub_receiver

    if not (0 < msg < n_r):
        raise ValueError("Message must be in range (0, n_receiver)")

    signature = rsa_sign(msg, d_s, n_s)
    encrypted_msg = rsa_encrypt(msg, e_r, n_r)
    encrypted_sig = rsa_encrypt(signature, e_r, n_r)

    return encrypted_msg, encrypted_sig

def receive_key(enc_msg, enc_sig, pub_sender, sec_receiver, pub_receiver):
    n_r, e_r = pub_receiver
    d_r = sec_receiver[0]
    n_s, e_s = pub_sender

    msg = rsa_decrypt(enc_msg, d_r, n_r)
    sig = rsa_decrypt(enc_sig, d_r, n_r)
    ok = rsa_verify(msg, sig, e_s, n_s)

    return msg, ok

def main_demo():
    print("Generating RSA keys...\n")

    pubA, secA = make_keypair(256)
    pubB, secB = make_keypair(256)

    nA, eA = pubA
    dA = secA[0]
    nB, eB = pubB
    dB = secB[0]

    k = secrets.randbelow(min(nA, nB) - 2) + 1

    print("Subscriber A")
    print(f"n_A = {nA}")
    print(f"e_A = {eA}")
    print(f"d_A = {dA}\n")

    print("Subscriber B")
    print(f"n_B = {nB}")
    print(f"e_B = {eB}")
    print(f"d_B = {dB}\n")

    print("Original transmitted key")
    print(f"k = {k}\n")

    enc_msg, enc_sig = send_key(k, pubA, secA, pubB)
    sig = rsa_sign(k, dA, nA)

    print("Sender A sends:")
    print(f"signature = {sig}")
    print(f"encrypted_message = {enc_msg}")
    print(f"encrypted_signature = {enc_sig}\n")
    
    received_k, ok = receive_key(enc_msg, enc_sig, pubA, secB, pubB)
    
    print("Receiver B gets:")
    print(f"received key = {received_k}")
    print(f"signature valid = {ok}")

    print("\nCompleted" if received_k == k and ok else "\nProtocol failed")

if __name__ == "__main__":
    main_demo()