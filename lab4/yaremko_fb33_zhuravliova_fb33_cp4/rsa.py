import random

# --- Settings ---
# Small primes for pre-check (Trial Division)
SMALL_PRIMES = [
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
    73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151
]

# --- Arithmetic Functions ---

def power_mod(base, exp, mod):
    return pow(base, exp, mod)

def extended_gcd(a, b):
    if a == 0:
        return (b, 0, 1)
    g, x1, y1 = extended_gcd(b % a, a)
    return (g, y1 - (b // a) * x1, x1)

def mod_inverse(a, m):
    g, x, y = extended_gcd(a, m)
    if g != 1:
        raise Exception("Modular inverse does not exist.")
    return x % m

# --- Primality Testing ---

def is_prime_miller_rabin(p, k=40):
    if p < 2:
        return False
    for sp in SMALL_PRIMES:
        if p == sp:
            return True
        if p % sp == 0:
            return False

    d = p - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1

    for _ in range(k):
        a = random.randrange(2, p - 1)
        x = power_mod(a, d, p)
        if x == 1 or x == p - 1:
            continue
        composite = True
        for _ in range(s - 1):
            x = power_mod(x, 2, p)
            if x == p - 1:
                composite = False
                break
        if composite:
            return False
    return True

def get_random_prime(bits, max_tries=100000):
    tries = 0
    while True:
        tries += 1
        candidate = random.getrandbits(bits) | (1 << (bits - 1)) | 1
        if is_prime_miller_rabin(candidate):
            return candidate
        if tries >= max_tries:
            raise Exception("Prime generation failed.")

# --- RSA Primitives ---

def GenerateKeyPair(key_size):
    print(f"\n --- Gemerating {key_size}-bit primes ---")
    p = get_random_prime(key_size // 2)
    q = get_random_prime(key_size // 2)
    while p == q:
        q = get_random_prime(key_size // 2)

    n = p * q
    phi = (p - 1) * (q - 1)

    e = 65537
    if extended_gcd(e, phi)[0] != 1:
        e = 3
        while extended_gcd(e, phi)[0] != 1:
            e += 2

    d = mod_inverse(e, phi)
    
    print("\n --- RSA PARAMETERS ---")
    print(f" p = {p}")
    print(f" q = {q}")
    print(f" n = {n}")
    print(f" phi(n) = {phi}")
    print(f" e = {e}")
    print(f" d = {d}")
    return (e, n), (d, p, q)

def Encrypt(message, public_key):
    e, n = public_key
    if message >= n:
        raise ValueError("Message is too large for modulus n")
    return power_mod(message, e, n)

def Decrypt(ciphertext, private_key):
    d, p, q = private_key
    n = p * q
    return power_mod(ciphertext, d, n)

def Sign(message, private_key):
    d, p, q = private_key
    n = p * q
    if message >= n:
        raise ValueError("Message is too large for modulus n")
    return power_mod(message, d, n)

def Verify(message, signature, public_key):
    e, n = public_key
    decrypted_signature = power_mod(signature, e, n)
    return decrypted_signature == (message % n)

# --- Protocol Functions ---

def SendKey(k, sender_private_key, sender_public_key, receiver_public_key):
    _, n_s = sender_public_key
    _, n_r = receiver_public_key

    if n_r < n_s:
        raise ValueError("Protocol Error: n_B must be >= n_A")
    if k >= n_s:
        raise ValueError("Protocol Error: k must be < n_A")

    S = Sign(k, sender_private_key)
    k1 = Encrypt(k, receiver_public_key)
    S1 = Encrypt(S, receiver_public_key)
    return k1, S1

def ReceiveKey(packet, receiver_private_key, receiver_public_key, sender_public_key):
    k1, S1 = packet
    k = Decrypt(k1, receiver_private_key)
    S = Decrypt(S1, receiver_private_key)
    valid = Verify(k, S, sender_public_key)
    return k, valid

# --- Scenarios ---

def run_lab_scenario():
    print("\n" + "="*50)
    print(" 1. AUTOMATIC PROTOCOL TEST")
    print("="*50)

    print(" > Generating keys for User A and B...", end=" ")
    pub_A, priv_A = GenerateKeyPair(256)
    while True:
        pub_B, priv_B = GenerateKeyPair(260)
        if pub_B[1] >= pub_A[1]:
            break
    print("Done.")
    
    print("\n === ENCRYPTION / DECRYPTION TEST ===")
    msg = random.randint(1, pub_A[1] // 2)
    print(f"- Messege: {msg}")
    
    c = Encrypt(msg, pub_B)
    print(f"- Ciphertext for B: {c}")
    
    dec = Decrypt(c, priv_B)
    print(f"- Decrypted by B: {dec}")
    
    print("\n === DIGITAL SIGNATURE TEST ===")
    sig = Sign(msg, priv_A)
    ok = Verify(msg, sig, pub_A)
    print(f"- Signature: {sig}")
    print(f"- Verify: {ok}")
    
    print("\n === KEY DISTRIBUTION PROTOCOL (A -> B) ===")
    k_secret = random.randint(1, pub_A[1] // 2)
    packet = SendKey(k_secret, priv_A, pub_A, pub_B)
    k_rec, valid = ReceiveKey(packet, priv_B, pub_B, pub_A)
    print(f"- Secret key k chosen by A = {k_secret}")
    print(f"- Encrypted k sent to B = {packet[0]}")
    print(f"- Signed k sent to B = {packet[1]}")
    print(f"- Received k by B = {k_rec}")
    print(f"- Signature valid? = {valid}")

    if k_rec == k_secret and valid:
        print(" [RESULT] SUCCESS: Keys are IDENTICAL and Authenticated.")
    else:
        print(" [RESULT] FAILURE.")

if __name__ == "__main__":
    run_lab_scenario()