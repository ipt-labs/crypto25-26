import argparse
from colorama import Fore, Style
from primes_gen import generate_strong_prime
from styles import print_error, print_green_blue_colored_pair

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
    #TODO implement further program logic