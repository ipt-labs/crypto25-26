import random
from styles import *
from primes_gen import generate_strong_prime
from rsa import *
from requests import get

e = 2**16+1
API_URL = "http://asymcryptwebservice.appspot.com/rsa/"

def get_server_pub_key()->tuple[int,int]:
    url = API_URL + "serverKey"
    params = {"keySize":512}
    try:
        response = get(url = url, params=params).json()
        return (int(response['publicExponent'],16),int(response['modulus'],16))
    except Exception as e:
        print_error(str(e))
    return None

def api_encrypt(pt:int,e:int,n:int)->str:
    url = API_URL + "encrypt"
    params = {
        "modulus" : hex(n)[2:],
        "publicExponent":hex(e)[2:],
        "message": hex(pt)[2:],
    }
    try:
        response = get(url = url, params=params)
        response.raise_for_status()
        return int.from_bytes(bytes.fromhex(response.json()['cipherText']))
    except Exception as e:
        print_error(str(e))
    return None

def api_decrypt():
    pass

def api_send_key():
    pass

def api_recv_key():
    pass

def api_sign(pt:int) -> int:
    url = API_URL + "sign"
    params = {
        "message": hex(pt)[2:]
    }
    try:
        response = get(url = url, params=params)
        print(response.text)
        response.raise_for_status()
        return int.from_bytes(bytes.fromhex(response.json()['signature']))
    except Exception as e:
        print_error(str(e))
    return None

def api_verify(pt:int,s:int,e:int,n:int)->bool:
    url = API_URL + "verify"
    params = {
        "modulus" : hex(n)[2:],
        "publicExponent":hex(e)[2:],
        "message": hex(pt)[2:],
        "signature": hex(s)[2:]
    }
    try:
        response = get(url = url, params=params)
        response.raise_for_status()
        return response.json()['verified']
    except Exception as e:
        print_error(str(e))
    return False

def test_with_remote_api(p:int,q:int):
    key_pair = gen_key_pair(p,q, e)
    print_green_blue_colored_pair("Public key:", key_pair.pub_key)
    print_green_blue_colored_pair("Private key:", key_pair.priv_key)

    pt = random.randrange(1,p*q)
    print_green_blue_colored_pair("Message:",pt)

    print_green_blue_colored_pair("Local encryption with pub key:", encrypt(pt,key_pair.pub_key[0],key_pair.pub_key[1]))
    print_green_blue_colored_pair("Remote encryption with pub key:", api_encrypt(pt,key_pair.pub_key[0],key_pair.pub_key[1]))

    s = sign(pt, key_pair.priv_key[0],key_pair.pub_key[1])
    print_green_blue_colored_pair("Signed message from client:",s)
    print_green_blue_colored_pair("Verified:", api_verify(s[0],s[1],key_pair.pub_key[0],key_pair.pub_key[1]))

    server_pub_key = get_server_pub_key()
    print_green_blue_colored_pair("Server pub key:", server_pub_key)

    s = api_sign(pt)
    print_green_blue_colored_pair("Signed message from server", s)
    print_green_blue_colored_pair("Verified:", verify(pt,s,server_pub_key[0],server_pub_key[1]))

if __name__ == "__main__":
    p1 = generate_strong_prime(bits=256)
    q1 = generate_strong_prime(bits=256)
    print_green_blue_colored_pair("P1:", p1)
    print_green_blue_colored_pair("Q1:", q1)
    p, q = None, None
    while True:
        p = generate_strong_prime(bits=256)
        max_q = (p1 * q1) // p
        min_q = 2 ** 255
        if max_q < min_q:
            continue
        q = generate_strong_prime(start=min_q, end=max_q)
        break
    print_green_blue_colored_pair("P:", p)
    print_green_blue_colored_pair("Q:", q)
    print(p*q <= p1*q1)
   
    test_with_remote_api(p,q)