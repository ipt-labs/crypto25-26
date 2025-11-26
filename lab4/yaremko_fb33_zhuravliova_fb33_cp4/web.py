import random
import requests

SMALL_PRIMES = [
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
    73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151
]

BASE_URL = "https://asymcryptwebservice.appspot.com"
session = requests.Session()

def power_mod(a, b, n): 
    return pow(a, b, n)

def extended_gcd(a, b):
    if a == 0:
        return (b, 0, 1)
    g, x1, y1 = extended_gcd(b % a, a)
    return (g, y1 - (b // a) * x1, x1)

def mod_inverse(a, m):
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise Exception("Inverse does not exist")
    return x % m

def is_prime_miller_rabin(p, k=40):
    if p < 2:
        return False
    for sp in SMALL_PRIMES:
        if p == sp:
            return True
        if p % sp == 0:
            return False

    d, s = p - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1

    for _ in range(k):
        a = random.randrange(2, p - 1)
        x = power_mod(a, d, p)
        if x == 1 or x == p - 1:
            continue
        
        for _ in range(s - 1):
            x = power_mod(x, 2, p)
            if x == p - 1:
                break
        else:
            return False

    return True

def get_random_prime(bits):
    while True:
        candidate = random.getrandbits(bits) | (1 << (bits - 1)) | 1
        if is_prime_miller_rabin(candidate):
            return candidate

def GenerateKeyPair(key_size):
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

    print("\n[LOCAL]:")
    print(f" n = {n} (hex = {format(n,'x')})")
    print(f" e = {e} (hex = {format(e,'x')})")
    return (e, n), (d, p, q)

def Encrypt(message, public_key):
    e, n = public_key
    if message >= n:
        raise ValueError("Message is too large for modulus n")
    return power_mod(message, e, n)

def Decrypt(ciphertext, private_key):
    d, p, q = private_key
    return power_mod(ciphertext, d, p * q)

def Sign(message, private_key):
    d, p, q = private_key
    return pow(message, d, p * q)

def Verify(message, signature, public_key):
    e, n = public_key
    return pow(signature, e, n) == message

def get_server_key(key_size=256):
    resp = session.get(f"{BASE_URL}/rsa/serverKey", params={"keySize": key_size})
    data = resp.json()
    print("\n[SERVER]:")
    print(" N =", data['modulus'])
    print(" E =", data['publicExponent'])
    return int(data["publicExponent"], 16), int(data["modulus"], 16)

def server_encrypt(n_hex, e_hex, m_hex):
    resp = session.get(f"{BASE_URL}/rsa/encrypt",
                       params={"modulus": n_hex, "publicExponent": e_hex, "message": m_hex, "type":"BYTES"})
    return int(resp.json()["cipherText"], 16)

def server_decrypt(cipher_hex):
    resp = session.get(f"{BASE_URL}/rsa/decrypt", params={"cipherText": cipher_hex})
    return int(resp.json()["message"], 16)

def server_sign(message_hex):
    resp = session.get(f"{BASE_URL}/rsa/sign", params={"message": message_hex, "type":"BYTES"})
    return int(resp.json()["signature"], 16)

def server_verify(n_hex, e_hex, message_hex, signature_hex):
    resp = session.get(f"{BASE_URL}/rsa/verify", params={"modulus": n_hex, "publicExponent": e_hex,
                                                         "message": message_hex, "signature": signature_hex, "type":"BYTES"})
    return resp.json()["verified"]

def server_send_key(n_hex, e_hex):
    resp = session.get(f"{BASE_URL}/rsa/sendKey", params={"modulus": n_hex, "publicExponent": e_hex})
    data = resp.json()
    return int(data["key"], 16), int(data["signature"], 16)

def server_receive_key(key_hex, sig_hex, n_hex, e_hex):
    resp = session.get(f"{BASE_URL}/rsa/receiveKey",
                       params={"key": key_hex, "signature": sig_hex, "modulus": n_hex, "publicExponent": e_hex})
    data = resp.json()
    return int(data["key"], 16), data["verified"]

def run_web_tests():
    print("\n" + "="*70)
    print("  2. WEB TESTS WITH RSA SERVICE ")
    print("="*70)

    pub_local, priv_local = GenerateKeyPair(256)
    e_loc, n_loc = pub_local

    pub_srv = get_server_key(256)
    e_srv, n_srv = pub_srv

    msg = random.randint(1, 2**64 - 1)
    print(f"\n Messange: {msg} (hex = {format(msg,'x')})")

    print("\n TEST 1: Local Encrypt -> Server Decrypt")
    c = Encrypt(msg, pub_srv)
    print(" Cipher (hex):", format(c,'x'))
    m_dec = server_decrypt(format(c,'x'))
    print(" Server decrypted:", m_dec)
    print(" Result:", "OK" if m_dec == msg else "FAIL")

    print("\n TEST 2: Server Encrypt -> Local Decrypt")
    c2 = server_encrypt(format(n_loc,'x'), format(e_loc,'x'), format(msg,'x'))
    print(" Cipher from server:", format(c2,'x'))
    m2 = Decrypt(c2, priv_local)
    print(" Local decrypted:", m2)
    print(" Result:", "OK" if m2 == msg else "FAIL")

    print("\n TEST 3: Local Sign -> Server Verify")
    sig = Sign(msg, priv_local)
    print(" Local signature:", format(sig,'x'))
    ok_v = server_verify(format(n_loc,'x'), format(e_loc,'x'), format(msg,'x'), format(sig,'x'))
    print(" Verification:", ok_v)
    print(" Result:", "OK" if ok_v else "FAIL")

    print("\n TEST 4: Server Sign -> Local Verify")
    sig2 = server_sign(format(msg,'x'))
    print(" Server signature:", format(sig2,'x'))
    ver_local = Verify(msg, sig2, pub_srv)
    print(" Local verification:", ver_local)
    print(" Result:", "OK" if ver_local else "FAIL")
    
    print("\n TEST 5: Client -> Server Key Exchange")
    k = random.randint(1, 2**64 - 1)
    print(f" Key sent = {k} (hex {format(k,'x')})")
    sig_k = Sign(k, priv_local)
    enc_k = Encrypt(k, pub_srv)
    enc_sig = Encrypt(sig_k, pub_srv)
    r_k, r_ok = server_receive_key(format(enc_k,'x'), format(enc_sig,'x'), format(n_loc,'x'), format(e_loc,'x'))
    print(" Server received key:", r_k)
    print(" Signature valid:", r_ok)
    print(" Result:", "OK" if r_k == k and r_ok else "FAIL")

    print("\n TEST 6: Server -> Client Key Exchange")
    enc_k2, enc_s2 = server_send_key(format(n_loc,'x'), format(e_loc,'x'))
    k2 = Decrypt(enc_k2, priv_local)
    s2 = Decrypt(enc_s2, priv_local)
    print(" Key received:", k2)
    print(" Signature valid:", Verify(k2, s2, pub_srv))
    print(" Result:", "OK" if Verify(k2, s2, pub_srv) else "FAIL")

    print("\n" + "="*70)
    print(" FINAL RESULT: WEB PROTOCOL TESTING COMPLETED!")
    print("="*70)

if __name__ == "__main__":
    run_web_tests()