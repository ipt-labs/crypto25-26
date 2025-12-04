import secrets
import math
from typing import Tuple, Optional, List

def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    if b == 0:
        return a, 1, 0
    g, x1, y1 = extended_gcd(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    return g, x, y

def modinv(a: int, m: int) -> Optional[int]:
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        return None
    return x % m

def is_probable_prime(n: int, k: int = 8) -> bool:
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

    for _ in range(k):
        a = secrets.randbelow(n - 3) + 2 
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
            if x == 1:
                return False
        else:
            return False
    return True

def generate_prime(bits: int, k: int = 8, max_failed_store: int = 30) -> int:
    if bits < 2:
        raise ValueError("bits must be >= 2")
    lower = 1 << (bits - 1)
    upper = (1 << bits) - 1
    failed: List[int] = []

    while True:
        candidate = secrets.randbits(bits) | (1 << (bits - 1)) | 1
        if candidate > upper:
            candidate = candidate >> 1
        if is_probable_prime(candidate, k=k):
            if failed:
                print(f"Candidates that failed primality test (last {len(failed[-max_failed_store:])}): {failed[-max_failed_store:]} (total {len(failed)})")
            return candidate
        else:
            failed.append(candidate)

def generate_keypair(bits: int = 256) -> Tuple[Tuple[int,int], Tuple[int,int,int]]:
    p = generate_prime(bits)
    q = generate_prime(bits)
    while q == p:
        q = generate_prime(bits)

    n = p * q
    phi = (p - 1) * (q - 1)
    e = 65537
    if math.gcd(e, phi) != 1:
        while True:
            e = secrets.randbelow(phi - 2) + 2
            if math.gcd(e, phi) == 1:
                break

    d = modinv(e, phi)
    if d is None:
        raise RuntimeError("Failed to find modular inverse for phi")

    return (n, e), (d, p, q)

def encrypt(m: int, e: int, n: int) -> int:
    return pow(m, e, n)

def decrypt(c: int, d: int, n: int) -> int:
    return pow(c, d, n)

def sign(m: int, d: int, n: int) -> int:
    return pow(m, d, n)

def verify_signature(m: int, s: int, e: int, n: int) -> bool:
    return m == pow(s, e, n)

def send_key(message: int, sender_public: Tuple[int,int], sender_secret: Tuple[int,int,int],
             receiver_public: Tuple[int,int]) -> Tuple[int,int]:
    n_sender, e_sender = sender_public
    d_sender = sender_secret[0]
    n_receiver, e_receiver = receiver_public

    if not (0 < message < n_receiver):
        raise ValueError("Message must be in range (0, n_receiver)")

    signature = sign(message, d_sender, n_sender)
    encrypted_signature = encrypt(signature, e_receiver, n_receiver)
    encrypted_message = encrypt(message, e_receiver, n_receiver)
    return encrypted_message, encrypted_signature

def receive_key(encrypted_message: int, encrypted_signature: int,
                sender_public: Tuple[int,int],
                receiver_secret: Tuple[int,int,int],
                receiver_public: Tuple[int,int]) -> Tuple[int, bool]:
    n_receiver, e_receiver = receiver_public
    d_receiver = receiver_secret[0]
    n_sender, e_sender = sender_public

    message = decrypt(encrypted_message, d_receiver, n_receiver)
    signature = decrypt(encrypted_signature, d_receiver, n_receiver)
    is_valid = verify_signature(message, signature, e_sender, n_sender)
    return message, is_valid

def sender_protocol(k: int, sender_public: Tuple[int,int], sender_secret: Tuple[int,int,int],
                    receiver_public: Tuple[int,int]) -> Tuple[int,int]:
    encrypted_message, encrypted_signature = send_key(k, sender_public, sender_secret, receiver_public)
    return encrypted_message, encrypted_signature

def receiver_protocol(encrypted_message: int, encrypted_signature: int,
                      sender_public: Tuple[int,int], 
                      receiver_secret: Tuple[int,int,int],
                      receiver_public: Tuple[int,int]) -> Tuple[int,bool]:
    k, is_valid = receive_key(encrypted_message, encrypted_signature, sender_public, receiver_secret, receiver_public)
    return k, is_valid

if __name__ == "__main__":
    print("Generating RSA keys...\n")

    pub_A, sec_A = generate_keypair(bits=256)
    pub_B, sec_B = generate_keypair(bits=256)

    n_A, e_A = pub_A
    d_A = sec_A[0]

    n_B, e_B = pub_B
    d_B = sec_B[0]

    k = secrets.randbelow(min(n_A, n_B) - 1) + 1

    print("=== Subscriber A ===")
    print(f"n_A = {n_A}")
    print(f"e_A = {e_A}")
    print(f"d_A = {d_A}\n")

    print("=== Subscriber B ===")
    print(f"n_B = {n_B}")
    print(f"e_B = {e_B}")
    print(f"d_B = {d_B}\n")

    print("=== Original transmitted key (message) ===")
    print(f"message (k) = {k}\n")

    encrypted_message, encrypted_signature = sender_protocol(
        k, pub_A, sec_A, pub_B
    )

    signature = sign(k, d_A, n_A)

    print("=== Sender A forms ===")
    print(f"signature = {signature}")
    print(f"encrypted_message = {encrypted_message}")
    print(f"encrypted_signature = {encrypted_signature}\n")

    received_key, is_valid = receiver_protocol(
        encrypted_message,
        encrypted_signature,
        pub_A,
        sec_B,
        pub_B
    )

    print("=== Receiver B gets ===")
    print(f"received_key = {received_key}")
    print(f"signature valid = {is_valid}")

    if received_key == k and is_valid:
        print("\nProtocol completed successfully")
    else:
        print("\nProtocol failed")