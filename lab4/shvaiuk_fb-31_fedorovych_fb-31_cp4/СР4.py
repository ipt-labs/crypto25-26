import random

trivial_prime = [2, 3, 5, 7, 11, 13, 17, 19, 23,
                 29, 31, 37, 41, 43, 47, 53, 59,
                 61, 67, 71, 73, 79, 83, 89, 97]


def gcd_(a, b):
    """ Euclid algorithm to find gcd """

    if a == 0:
        return b, 0, 1

    gcd, v1, u1 = gcd_(b % a, a)
    u = u1 - (b // a) * v1
    v = v1

    return gcd, u, v


def find_reverse_a(a, m):
    """ Find a**-1 mod m """

    g, x, y = gcd_(a, m)

    if g != 1:
        return None
    else:
        return x % m


def solve_linear_congruence(a, b, m):
    """ Solve ax = b mod(m) """

    gcd, x, y = gcd_(a, m)

    if not b % gcd == 0:
        return []
    else:
        a = a // gcd
        b = b // gcd
        m = m // gcd

        x = b * find_reverse_a(a, m) % m
        solutions = [(x + m * k) for k in range(gcd)]  # x_formula = x + m*k, k є Z

        return solutions


def euler_phi(n):
    """ Calculate φ(n) """

    result = n
    p_ = 2

    while p_ * p_ <= n:
        if n % p_ == 0:
            while n % p_ == 0:
                n //= p_
            result -= result // p_
        p_ += 1
    if n > 1:
        result -= result // n

    return result


def horny_power(x, y, mod):
    """ Horner scheme for finding (x**y) mod m """

    result = 1

    while y > 0:
        if y % 2 == 1:
            result = (result * x) % mod
        x = (x * x) % mod
        y //= 2

    return result


def if_prime_trial_div(n):
    """ Check if the number is prime using trial division """

    global trivial_prime

    if n < 2:
        return False
    for i in trivial_prime:
        if n % i == 0:
            return False
    return True


def if_prime_mil_rab(p_, k):
    """ Check if the number is prime using Miller-Rabin algorithm """

    if p_ == 2 or p_ == 3:
        return True
    if p_ % 2 == 0:
        return False

    s, d_ = 0, p_ - 1
    while d_ % 2 == 0:
        s += 1
        d_ //= 2

    for _ in range(k):
        a = random.randint(2, p_ - 2)
        x = horny_power(a, d_, p_)

        if x == 1 or x == p_ - 1:
            continue

        for _ in range(s - 1):
            x = horny_power(x, 2, p_)
            if x == p_ - 1:
                break
        else:
            return False
    return True


def generate_prime(bits=256, k=20, interval=False):
    """ Generate a random number of specific (256) bit """

    if interval:
        candidate = random.randint(10 ** 77, int("9" * 78))
    else:
        candidate = random.getrandbits(bits)
        candidate |= (1 << bits - 1) | 1

    if if_prime_trial_div(candidate):
        if if_prime_mil_rab(candidate, k):
            return candidate
        else:
            return generate_prime(bits, k, interval=interval)
    else:
        return generate_prime(bits, k, interval=interval)


def generate_p_q(bits=256, interval=False):
    """ Generate (p, q) and (p_1, q_1) which are suitable """

    p_ = generate_prime(bits, 20, interval=interval)
    q_ = generate_prime(bits, 20, interval=interval)
    p_1_ = generate_prime(bits, 20, interval=interval)
    q_1_ = generate_prime(bits, 20, interval=interval)

    while p_ * q_ > p_1_ * q_1_:
        print(f"These candidates are invalid:\np = {p_}\nq = {q_}\np_1 = {p_1_}\nq_1 = {q_1_}")
        return generate_p_q(interval=interval)

    return p_, q_, p_1_, q_1_


def GenerateKeyPair(p_, q_):
    """ Generate key-pair for a user """

    n_ = p_ * q_
    phi = (p_ - 1) * (q_ - 1)
    e_ = 2**16+1
    while gcd_(e_, phi)[0] != 1:
        e_ = random.randint(2, phi - 1)

    d_ = find_reverse_a(e_, phi)

    return (d_, p_, q_), (n_, e_)


def Encrypt(M_, pubkey):
    """ Encrypt valid message using C = (M**e) mod n formula """

    if not isinstance(M_, int):  # convert str to int
        M_ = int.from_bytes(M_.encode('utf-8'), byteorder='big')

    if 0 <= M_ <= pubkey[0] - 1:
        C_ = horny_power(M_, pubkey[1], pubkey[0])
        return C_
    else:
        return None


def Decrypt(C_, privkey, text=False):
    """ Decrypt valid message using M = (C**d) mod n """

    n_ = privkey[1] * privkey[2]

    if 0 <= C_ <= n_ - 1:
        M_ = horny_power(C_, privkey[0], n_)

        if text:
            return M_.to_bytes((M_.bit_length() + 7) // 8, byteorder='big').decode('utf-8')
        else:
            return M_
    else:
        return None


def Sign(M_, privkey):
    """ A digital signature for a message """

    if not isinstance(M_, int):  # convert str to int
        M_ = int.from_bytes(M_.encode('utf-8'), byteorder='big')

    S_ = horny_power(M_, privkey[0], privkey[1] * privkey[2])

    return (M_, S_)


def Verify(signature, pubkey):
    """ Verify the signed message """

    M_ = signature[0]
    S_ = signature[1]

    if not isinstance(M_, int):
        M_ = int.from_bytes(M_.encode('utf-8'), byteorder='big')

    M__ = horny_power(S_, pubkey[1], pubkey[0])

    return M_ == M__


def SendKey(k_, pubkey_a, privkey_a, pubkey_b):
    """ Send keys using public pipe """

    k_1_ = Encrypt(k_, pubkey_b)
    S_ = Sign(k_, privkey_a)
    S_1_ = Encrypt(S_[1], pubkey_b)

    return (k_1_, S_1_)


def ReceiveKey(received, privkey_b, pubkey_a):
    """ Receive keys using public pipe """

    k_1_ = received[0]
    S_1_ = received[1]

    k_ = Decrypt(k_1_, privkey_b)
    S_ = Decrypt(S_1_, privkey_b)

    if Verify((k_, S_), pubkey_a):
        print("k is verified")
        return (k_, S_)
    else:
        print("k could not be verified")
        return None


PURPLE = "\033[95m"
CYAN = "\033[96m"
PINK = "\033[95m"
RESET = "\033[0m"

def print_section(title, color=PURPLE):
    print(f"\n{color}╭{'─'*48}╮{RESET}")
    print(f"{color}│{title.center(48)}│{RESET}")
    print(f"{color}╰{'─'*48}╯{RESET}")

def print_keys(public_key, private_key, user="A"):
    print_section(f"Keys for User {user}", PURPLE)
    print(f"{CYAN}{'Public key:':<20}{RESET} {public_key}")
    print(f"{CYAN}{'Private key:':<20}{RESET} {private_key}")

def print_large_numbers_clean(p, q, label="p/q"):
    print_section(f"{label} Numbers", PINK)
    print(f"{CYAN}p:{RESET} {p} (len={len(bin(p)[2:])})")
    print(f"{CYAN}q:{RESET} {q} (len={len(bin(q)[2:])})")


if __name__ == "__main__":
    # ---------- Generate p, q, p_1, q_1 ----------
    print_section("Generating Valid Numbers", CYAN)
    p, q, p_1, q_1 = generate_p_q(bits=256, interval=False)
    print(f"{CYAN}p * q <= p_1 * q_1:{RESET} {p * q <= p_1 * q_1}")
    print(f"{CYAN}p:{RESET} {p}")
    print(f"{CYAN}q:{RESET} {q}")
    print(f"{CYAN}p_1:{RESET} {p_1}")
    print(f"{CYAN}q_1:{RESET} {q_1}")
    print(f"{CYAN}len of p_1:{RESET} {len(bin(p_1)[2:])} \n{CYAN}len of q_1:{RESET} {len(bin(q_1)[2:])}")

    # ---------- Static large numbers ----------
    p = 62292051873732111696239942114403170513866646571234155956926929905487334616531
    q = 107856527211449048964097072747761105850090651956211176122828103303232450011733
    p_1 = 102212875132880649877270819301141701576819197983714203788291325382307197654689
    q_1 = 79788335472330262274200476827445331604017075565917214625517614772660663877009

    print_large_numbers_clean(p, q, "User A Static")
    print_large_numbers_clean(p_1, q_1, "User B Static")
    print(f"\np * q <= p_1 * q_1 : {p * q <= p_1 * q_1}")

    # ---------- Generate keys ----------
    keys_a = GenerateKeyPair(p, q)
    keys_b = GenerateKeyPair(p_1, q_1)

    public_key_a, private_key_a = keys_a[1], keys_a[0]
    public_key_b, private_key_b = keys_b[1], keys_b[0]

    print_keys(public_key_a, private_key_a, "A")
    print_keys(public_key_b, private_key_b, "B")

    # ---------- Encryption / Decryption ----------
    M = 'Hello Mario'
    print_section("Testing Encryption/Decryption", CYAN)
    print(f"Original Message: {M}")

    cryptogram_a = Encrypt(M, public_key_b)
    cryptogram_b = Encrypt(M, public_key_a)

    decrypted_a = Decrypt(cryptogram_b, private_key_a, text=True)
    decrypted_b = Decrypt(cryptogram_a, private_key_b, text=True)

    print(f"Encrypted for B: {cryptogram_a}")
    print(f"Encrypted for A: {cryptogram_b}")
    print(f"Decrypted by A: {decrypted_a}")
    print(f"Decrypted by B: {decrypted_b}")

    # ---------- Digital Signatures ----------
    signed_a = Sign(M, private_key_a)
    signed_b = Sign(M, private_key_b)

    print_section("Testing Signatures", PINK)
    print(f"Signature by A: {signed_a}")
    print(f"Signature by B: {signed_b}")

    verification_a = Verify(signed_a, public_key_a)
    verification_b = Verify(signed_b, public_key_b)

    print(f"Verification for A: {verification_a}")
    print(f"Verification for B: {verification_b}")

    # ---------- Key Exchange ----------
    k = random.randint(0, public_key_a[0])
    k_encrypted = Encrypt(k, public_key_a)
    k_sign = Sign(k, private_key_a)
    sent = SendKey(k, public_key_a, private_key_a, public_key_b)
    received = ReceiveKey(sent, private_key_b, public_key_a)
    b_verify = Verify(k_sign, public_key_a)

    print_section("Key Exchange Test", CYAN)
    print(f"Original k: {k}")
    print(f"Encrypted k to send: {k_encrypted}")
    print(f"Signed k by A: {k_sign}")
    print(f"Sent by A: {sent}")
    print(f"Received by B: {received}")
    print(f"Verification of k_sign by B: {b_verify}")

    # ---------- Server-side testing ----------
    print_section("Server-Side Testing", PURPLE)

    p, q, p_1, q_1 = generate_p_q(bits=128, interval=False)
    p = 181207594698208181078258173571185530019
    q = 295474412342678748021019178493214795663

    keys_a = GenerateKeyPair(p, q)
    public_key_a, private_key_a = keys_a[1], keys_a[0]

    pubkey_serv = (int("B10E187991D7A747EACBD41E1512F7B0806B351977A519098A45CA1F5E65019D", 16), int("10001", 16))
    message = 'Hello Mario'

    ciphertext_serv = int("4DCDC64B3D041F985D660DB395C6E80E4B291D53F0FF1AE9F41551B1B746D1B0", 16)
    ciphertext_our = Encrypt(message, pubkey_serv)

    print(f"{CYAN}Ciphertext encrypted by server:{RESET} {ciphertext_serv}")
    print(f"{CYAN}Ciphertext encrypted by us:     {RESET} {ciphertext_our}")
    num = 35191661563389491328066706556295523188501236257476625263176739061819916079536
    print(f"{PINK}Hex value:{RESET} {hex(num)}")
    print(f"{PINK}Public key a:{RESET} {public_key_a}")
    print(f"{PINK}Private key a:{RESET} {private_key_a}")
    print(f"{PINK}Public key a in hex:{RESET} ({hex(public_key_a[0])}, {hex(public_key_a[1])})")
    print(f"{PINK}Private key a in hex:{RESET} ({hex(private_key_a[0])}, {hex(private_key_a[1])}, {hex(private_key_a[2])})")

    print(
        f"{CYAN}Decrypted with our key:         {RESET} {Decrypt(int('75985089BE1004238206DDDF5D32AD4828B8CBB0F0E1020C1B6A8174E47CA735', 16), private_key_a, text=True)}")
    print(
        f"{CYAN}Server signature verified:      {RESET} {Verify((message, int('8F61EE3863F5E067C47AB2AF272962C56981820117A03F22E25971C84A27C487', 16)), pubkey_serv)}")
    generated_sign = Sign(message, private_key_a)
    print(f"{CYAN}Our generated signature (hex):  {RESET} {hex(generated_sign[1])}")
    print(f"{CYAN}k is verified{RESET}")

    print(f"{CYAN}Received key:{RESET}")
    received = ReceiveKey((int('5B39213FD1B35D81CBD84937835B65EB3C4C1E275F19E015B2828D3E023E38D7', 16),
                           int('694883EE7AF784A5EA11EF55369384DFADB9015B9092F0B78DAED9D485653B4E', 16)),
                          private_key_a, pubkey_serv)
    print(f"  {hex(received[0])},")
    print(f"  {hex(received[1])}")

    sent = SendKey(message, public_key_a, private_key_a, pubkey_serv)
    print(f"{CYAN}Sent key:{RESET}")
    print(f"  {hex(sent[0])},")
    print(f"  {hex(sent[1])}")

    key_ = 0x48656C6C6F204D6172696F
    print(f"{CYAN}Key as text:{RESET} {key_.to_bytes((key_.bit_length() + 7) // 8, byteorder='big').decode('utf-8')}")

