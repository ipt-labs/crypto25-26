from styles import *
from primes_gen import generate_strong_prime
from rsa import *
from requests import request

API_URL = "http://asymcryptwebservice.appspot.com/rsa/"

def get_server_pub_key():
    pass

def api_encrypt(pt:int,e:int,n:int):
    url = API_URL + "encrypt"
    params = {
        "modulus" : n,
        "publicExponent": e,
        "message": pt
    }
    try:
        response = request(url, params=params)
    except Exception as e:
        print_error(e)

def api_decrypt():
    pass

def api_send_key():
    pass

def api_recv_key():
    pass

def api_sign():
    pass

def api_url():
    pass

def test_with_remote_api(p:int,q:int):
    key_pair = gen_key_pair(p,q, e)
    print_green_blue_colored_pair("Public key: ", key_pair.pub_key)
    print_green_blue_colored_pair("Private key", key_pair.priv_key)



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