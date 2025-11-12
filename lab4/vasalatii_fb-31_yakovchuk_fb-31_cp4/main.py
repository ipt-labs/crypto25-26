import random
from styles import *
from primes_gen import generate_strong_prime
from rsa import *
from requests import get, Session

e = 2**16+1
API_URL = "http://asymcryptwebservice.appspot.com/rsa/"
session = Session()

def get_server_pub_key()->tuple[int,int]:
    url = API_URL + "serverKey"
    params = {"keySize":768}
    try:
        response = session.get(url = url, params=params).json()
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
        response = session.get(url = url, params=params)
        response.raise_for_status()
        return int.from_bytes(bytes.fromhex(response.json()['cipherText']))
    except Exception as e:
        print_error(str(e))
    return None

def api_decrypt(ct:int)->int:
    url = API_URL + "decrypt"
    params = {"cipherText":hex(ct)[2:]}
    try:
        response = session.get(url = url, params=params).json()
        return int(response['message'],16)
    except Exception as e:
        print_error(str(e))
    return None

def api_send_key(e:int,n:int)->tuple[int,int]:
    url = API_URL + "sendKey"
    params = {
        "modulus" : hex(n)[2:],
        "publicExponent":hex(e)[2:],
    }
    try:
        response = session.get(url = url, params=params)
        response.raise_for_status()
        response = response.json()
        return (int(response['key'],16),int(response['signature'],16))
    except Exception as e:
        print_error(str(e))
    return None

def api_recv_key(enc_k:int,sig:int,e:int,n:int):
    url = API_URL + "receiveKey"
    params = {
        "key":hex(enc_k)[2:],
        "signature": hex(sig)[2:],
        "modulus" : hex(n)[2:],
        "publicExponent":hex(e)[2:],
    }
    try:
        response = session.get(url = url, params=params)
        response.raise_for_status()
        response = response.json()
        return (int(response['key'],16),response['verified'])
    except Exception as e:
        print_error(str(e))
    return None

def api_sign(pt:int) -> int:
    url = API_URL + "sign"
    params = {
        "message": hex(pt)[2:]
    }
    try:
        response = session.get(url = url, params=params)
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
        response = session.get(url = url, params=params)
        response.raise_for_status()
        return response.json()['verified']
    except Exception as e:
        print_error(str(e))
    return False

def test_with_remote_api():
    server_pub_key = get_server_pub_key()
    print_green_blue_colored_pair("Server pub key:", server_pub_key)

    p = generate_strong_prime(bits=256)
    q = generate_strong_prime(bits=256)

    key_pair = gen_key_pair(p,q, e)
    print_green_blue_colored_pair("Public key:", key_pair.pub_key)
    print_green_blue_colored_pair("Private key:", key_pair.priv_key)

    pt_sm = random.randrange(1,server_pub_key[1])
    print_green_blue_colored_pair("Message:",pt_sm)

    ct =  encrypt(pt_sm,server_pub_key[0],server_pub_key[1])
    print_green_blue_colored_pair("Local encryption with pub key:", ct)
    print_green_blue_colored_pair("Decrypted message from server", api_decrypt(ct))

    pt_cm = random.randrange(1,key_pair.pub_key[1])
    print_green_blue_colored_pair("Message:",pt_cm)
    ct = api_encrypt(pt_cm,key_pair.pub_key[0],key_pair.pub_key[1])
    print_green_blue_colored_pair("Encrypted message from server:", ct)
    print_green_blue_colored_pair("Decrypted message:",decrypt(ct,key_pair.priv_key[0], key_pair.pub_key[1]))

    s = sign(pt_cm, key_pair.priv_key[0],key_pair.pub_key[1])
    print_green_blue_colored_pair("Signed message from client:",s)
    print_green_blue_colored_pair("Verified:", api_verify(s[0],s[1],key_pair.pub_key[0],key_pair.pub_key[1]))

    s = api_sign(pt_sm)
    print_green_blue_colored_pair("Sent to server:", pt_sm)
    print_green_blue_colored_pair("Signed message from server:", s)
    print_green_blue_colored_pair("Verified:", verify(pt_sm,s,server_pub_key[0],server_pub_key[1]))

    p1 = generate_strong_prime(bits=512)
    q1 = generate_strong_prime(bits=512)

    key_pair1 = gen_key_pair(p1,q1, e)
    print_green_blue_colored_pair("Public key:", key_pair1.pub_key)
    print_green_blue_colored_pair("Private key:", key_pair1.priv_key)
    
    s_k = api_send_key(key_pair1.pub_key[0],key_pair1.pub_key[1])
    print_green_blue_colored_pair("Received:", s_k)
    dec_key, s, verified = retrieve_key(
        s_k[0], s_k[1], key_pair1.priv_key[0], key_pair1.pub_key[1], server_pub_key[0],
        server_pub_key[1]
    )
    print_green_blue_colored_pair("Retrieved key:", (dec_key, s, verified))

    enc_key, enk_s = prep_key_for_sending(dec_key,key_pair.priv_key[0],key_pair.pub_key[1],server_pub_key[0],server_pub_key[1])
    print_green_blue_colored_pair("Sent key:", (enc_key,enk_s))
    print_green_blue_colored_pair("Server got:", api_recv_key(enc_key, enk_s, key_pair.pub_key[0],key_pair.pub_key[1]))


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
    # print(p*q <= p1*q1)
   
    test_with_remote_api()