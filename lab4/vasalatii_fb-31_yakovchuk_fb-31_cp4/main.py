import random
from typing import Any, Optional
from styles import *
from primes_gen import generate_strong_prime
from rsa import *
from requests import get, Session

API_URL = "http://asymcryptwebservice.appspot.com/rsa/"
session = Session()

def api_get(endpoint: str, params: dict[str,Any])->str|bool|int|tuple[int,int]|None:
    url = API_URL + endpoint
    try:
        response = session.get(url=url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print_error(f"Error during {endpoint}: {e}")
        if 'response' in locals():
            print_error(f"Response text: {response.text}")
        return None

def get_server_pub_key()->Optional[tuple[int,int]]:
    params = {"keySize":768}
    response = api_get("serverKey",params)
    if response is None:
        return None
    return (int(response['publicExponent'],16),int(response['modulus'],16))

def api_encrypt(pt:int,e:int,n:int)->Optional[str]:
    params = {
        "modulus" : hex(n)[2:],
        "publicExponent":hex(e)[2:],
        "message": hex(pt)[2:],
    }
    response = api_get("encrypt",params)
    if response is None:
        return None
    return int.from_bytes(bytes.fromhex(response['cipherText']))

def api_decrypt(ct:int)->Optional[int]:
    params = {"cipherText":hex(ct)[2:]}
    response = api_get("decrypt",params)
    if response is None:
        return None
    return int(response['message'],16)

def api_send_key(e:int,n:int)->Optional[tuple[int,int]]:
    params = {
        "modulus" : hex(n)[2:],
        "publicExponent":hex(e)[2:],
    }
    response = api_get("sendKey",params)
    if response is None:
        return None
    return (int(response['key'],16),int(response['signature'],16))

def api_recv_key(enc_k:int,sig:int,e:int,n:int)->Optional[tuple[int,int]]:
    params = {
        "key":hex(enc_k)[2:],
        "signature": hex(sig)[2:],
        "modulus" : hex(n)[2:],
        "publicExponent":hex(e)[2:],
    }
    response = api_get("receiveKey",params)
    if response is None:
        return None
    return (int(response['key'],16),response['verified'])

def api_sign(pt:int) -> Optional[int]:
    params = {
        "message": hex(pt)[2:]
    }
    response = api_get("sign",params)
    if response is None:
        return None
    return int.from_bytes(bytes.fromhex(response['signature']))

def api_verify(pt:int,s:int,e:int,n:int)->Optional[bool]:
    params = {
        "modulus" : hex(n)[2:],
        "publicExponent":hex(e)[2:],
        "message": hex(pt)[2:],
        "signature": hex(s)[2:]
    }
    response = api_get("verify",params)
    if response is None:
        return None
    return response['verified']

def test_with_remote_api():
    server_pub_key = get_server_pub_key()
    print_delimiter()
    print_green_blue_colored_pair("Server pub key:", server_pub_key)
    if server_pub_key is None:
        return

    key_pair = gen_key_pair(bits=512)
    print_delimiter()
    print_green_blue_colored_pair("Public key:", key_pair.pub_key)
    print_green_blue_colored_pair("Private key:", key_pair.priv_key)

    pt_sm = random.randrange(1,server_pub_key[1])
    print_delimiter()
    print_green_blue_colored_pair("Message:",pt_sm)

    ct =  encrypt(pt_sm,server_pub_key[0],server_pub_key[1])
    print_green_blue_colored_pair("Local encryption with pub key:", ct)
    pt_dec = api_decrypt(ct)
    if pt_dec is not None:
        print_green_blue_colored_pair("Decrypted message from server", pt_dec)

    pt_cm = random.randrange(1,key_pair.pub_key[1])
    ct = api_encrypt(pt_cm,key_pair.pub_key[0],key_pair.pub_key[1])
    if ct is not None:
        print_delimiter()
        print_green_blue_colored_pair("Message:",pt_cm)
        print_green_blue_colored_pair("Encrypted message from server:", ct)
        print_green_blue_colored_pair("Locally decrypted message:",decrypt(ct,key_pair.priv_key[0], key_pair.pub_key[1]))

    s = sign(pt_cm, key_pair.priv_key[0],key_pair.pub_key[1])
    print_delimiter()
    print_green_blue_colored_pair("Signed message from client:",s)
    ver = api_verify(s[0],s[1],key_pair.pub_key[0],key_pair.pub_key[1])
    if ver is not None:
        print_green_blue_colored_pair("Verified by server:", ver)

    s = api_sign(pt_sm)
    if pt_sm is not None:
        print_delimiter()
        print_green_blue_colored_pair("Sent to server:", pt_sm)
        print_green_blue_colored_pair("Signed message from server:", s)
        print_green_blue_colored_pair("Verified locally:", verify(pt_sm,s,server_pub_key[0],server_pub_key[1]))

    key_pair1 = gen_key_pair(bits=1024)
    print_delimiter()
    print_green_blue_colored_pair("Public key:", key_pair1.pub_key)
    print_green_blue_colored_pair("Private key:", key_pair1.priv_key)
    
    s_k = api_send_key(key_pair1.pub_key[0],key_pair1.pub_key[1])
    if s_k is not None:
        print_delimiter()
        print_green_blue_colored_pair("Received encrypted secret and signature:", s_k)
        dec_key, s, verified = retrieve_key(
            s_k[0], s_k[1], key_pair1.priv_key[0], key_pair1.pub_key[1], server_pub_key[0],
            server_pub_key[1]
        )
        print_green_blue_colored_pair("Retrieved key:", (dec_key, s))
        print_green_blue_colored_pair("Verified:", verified)

        enc_key, enk_s = prep_key_for_sending(dec_key,key_pair.priv_key[0],key_pair.pub_key[1],server_pub_key[0],server_pub_key[1])
        r_k = api_recv_key(enc_key, enk_s, key_pair.pub_key[0],key_pair.pub_key[1])
        if r_k is not None:
            print_delimiter()
            print_green_blue_colored_pair("Sent encrypted secret and signature:", (enc_key,enk_s))
            print_green_blue_colored_pair("Server got:", r_k[0])
            print_green_blue_colored_pair("Verified:",r_k[1])


def test_locally():
    print_delimiter()
    key_pair_a = gen_key_pair(bits=512)
    print_green_blue_colored_pair("A public key:", key_pair_a.pub_key)
    print_green_blue_colored_pair("A private key:", key_pair_a.priv_key)

    print_delimiter()
    key_pair_b = gen_key_pair(bits=512)
    while key_pair_a.pub_key[1] > key_pair_b.pub_key[1]:
        key_pair_b = gen_key_pair(bits=512)
        
    print_green_blue_colored_pair("B public key:", key_pair_b.pub_key)
    print_green_blue_colored_pair("B private key:", key_pair_b.priv_key)

    print_delimiter()
    pt = random.randrange(1,key_pair_a.pub_key[1])
    print_green_blue_colored_pair("Message:", pt)

    print_delimiter()
    ct = encrypt(pt,key_pair_a.pub_key[0],key_pair_a.pub_key[1])
    pt_dec = decrypt(ct,key_pair_a.priv_key[0],key_pair_a.pub_key[1])
    print_green_blue_colored_pair("Enc msg with A pub key:", ct)
    print_green_blue_colored_pair("Dec msg with A priv key:", pt_dec)

    print_delimiter()
    ct = encrypt(pt,key_pair_b.pub_key[0],key_pair_b.pub_key[1])
    pt_dec = decrypt(ct,key_pair_b.priv_key[0],key_pair_b.pub_key[1])
    print_green_blue_colored_pair("Enc msg with B pub key:", ct)
    print_green_blue_colored_pair("Dec msg with B priv key:", pt_dec)

    print_delimiter()
    _, s = sign(pt, key_pair_a.priv_key[0],key_pair_a.pub_key[1])
    print_green_blue_colored_pair("Signed message with A priv key:", s)
    print_green_blue_colored_pair("Verified:", verify(pt,s,key_pair_a.pub_key[0],key_pair_a.pub_key[1]))

    print_delimiter()
    _, s = sign(pt, key_pair_b.priv_key[0],key_pair_b.pub_key[1])
    print_green_blue_colored_pair("Signed message with B priv key:", s)
    print_green_blue_colored_pair("Verified:", verify(pt,s,key_pair_b.pub_key[0],key_pair_b.pub_key[1]))

    print_delimiter()
    key = random.randrange(1,2**63)
    print_green_blue_colored_pair("Key:",key)
    s_key, s = prep_key_for_sending(key, key_pair_a.priv_key[0],key_pair_a.pub_key[1], key_pair_b.pub_key[0],key_pair_b.pub_key[1])
    print_green_blue_colored_pair("Prepared key for sending:", (s_key, s))
    r_k = retrieve_key(s_key,s,key_pair_b.priv_key[0],key_pair_b.pub_key[1],key_pair_a.pub_key[0],key_pair_a.pub_key[1])
    print_green_blue_colored_pair("Retrieved key:", r_k[0])
    print_green_blue_colored_pair("Verified:",r_k[2])


if __name__ == "__main__":
    print_double_delimiter()
    print(Fore.LIGHTMAGENTA_EX + r"""
                                                    _                    _   _            _   
                                                   | |    ___   ___ __ _| | | |_ ___  ___| |_ 
                                                   | |   / _ \ / __/ _` | | | __/ _ \/ __| __|
                                                   | |__| (_) | (_| (_| | | | ||  __/\__ \ |_ 
                                                   |_____\___/ \___\__,_|_|  \__\___||___/\__|
                                             
        """ + Style.RESET_ALL)
    print_double_delimiter()
    test_locally()

    print_double_delimiter()
    print(Fore.LIGHTMAGENTA_EX + r"""
                                                       _    ____ ___   _            _   
                                                      / \  |  _ \_ _| | |_ ___  ___| |_ 
                                                     / _ \ | |_) | |  | __/ _ \/ __| __|
                                                    / ___ \|  __/| |  | ||  __/\__ \ |_ 
                                                   /_/   \_\_|  |___|  \__\___||___/\__|
                                      
        """ + Style.RESET_ALL)
    print_double_delimiter()
    test_with_remote_api()