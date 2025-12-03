# This script has no specific requirements
import random
from RSA import GenSmallPrimes, RandPrime, GenKeyPair, send, recv, SendKey, RecvKey

def main():
    small_primes = GenSmallPrimes()
    # 2^255 <= p < 2^256 - 256 бітне число
    n0 = 1 << 255
    n1 = (1 << 256) - 1

    p1  = RandPrime(small_primes, n0, n1)
    q1  = RandPrime(small_primes, n0, n1)

    p2 = RandPrime(small_primes, n0, n1)
    q2 = RandPrime(small_primes, n0, n1)

    if p1 * q1 <= p2 * q2:
        p_A, q_A, p_B, q_B = p1, q1, p2, q2
    else:
         p_B, q_B, p_A, q_A = p1, q1, p2, q2
    
    print(f"p_A: {p_A} \nq_A: {q_A}\n\np_B: {p_B} \nq_B: {q_B}")
    print("\n", "-"*100, "\n")

    pk_A, sk_A = GenKeyPair(p_A, q_A)
    pk_B, sk_B = GenKeyPair(p_B, q_B)
    n_A, e_A = pk_A
    n_B, e_B = pk_B
    d_A, _, _ = sk_A
    d_B, _, _ = sk_B
    print(f"n_A: {n_A} \ne_A: {e_A}\nd_A: {d_A}\n\nn_B: {n_B} \ne_B: {e_B} \nd_B: {d_B}")
    print("\n", "-"*100, "\n")

    # Протокол обміну шифрованих повідомлень з цифровим підписом
    print("A send number to B")
    n, _ = pk_A
    msg = random.randrange(1, n-1)
    packet1 = send(msg, sk_A, pk_B)

    print("\nA send text to B")
    text_msg = "I'm A"
    packet2 = send(text_msg, sk_A, pk_B)

    print("\nB recv number from A")
    r_msg1 = recv(packet1, sk_B, pk_A)
    print(f"recieved message {r_msg1}\n")

    print("nB recv text from A")
    r_msg2 = recv(packet2, sk_B, pk_A)
    print(f"recieved message {r_msg2}\n")

    print("B send number to A")
    packet3 = send(msg, sk_A, pk_B)

    print("\nA recv number from B")
    r_msg3 = recv(packet3, sk_B, pk_A)
    print(f"recieved message {r_msg3}")
    
    # Протокол конфіденційного розсилання ключів 
    print("\n", "-"*100, "\n")
    print("A send key to B")
    packet4, k1, pk_A, sk_A = SendKey(sk_A, pk_A, pk_B)
    print(f"sender saved key: {k1}\n")
    r_msg4 = RecvKey(packet4, sk_B, pk_A)
    print(f"reciever recieved key {r_msg4}\n")

    print("B send key to A")
    packet5, k2, pk_B, sk_B = SendKey(sk_B, pk_B, pk_A)
    print(f"sender saved key: {k2}\n")
    r_msg5 = RecvKey(packet5, sk_A, pk_B)
    print(f"reciever recieved key {r_msg5}")

if __name__ == "__main__":
    main()
