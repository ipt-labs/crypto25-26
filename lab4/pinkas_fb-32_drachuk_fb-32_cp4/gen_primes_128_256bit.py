# This script has no specific requirements
from RSA import GenSmallPrimes, RandPrime

def main():
    small_primes = GenSmallPrimes()
    n0 = 1 << 127
    n1 = (1 << 128) - 1
    n2 = 1 << 255
    n3 = (1 << 256) - 1

    p1  = RandPrime(small_primes, n0, n1)
    q1  = RandPrime(small_primes, n0, n1)
    p2  = RandPrime(small_primes, n2, n3)
    q2  = RandPrime(small_primes, n2, n3)

    print(f"p1: {p1} \nq1: {q1}\n\np2: {p2} \nq2: {q2}")

if __name__ == "__main__":
    main()