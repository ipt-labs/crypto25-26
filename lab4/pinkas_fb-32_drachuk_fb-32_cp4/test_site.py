# This script has no specific requirements
from RSA import GenKeyPair, Encrypt, Decrypt, miller_rabin_test, GenSmallPrimes, RandPrime
from math_mod import mod_gorner
import random

# мої прекрасні функції підпису і підтвердження підпису не підходять для сайту, так як він працює з повідомленнями, а не з хешем
def Sign_nohash(m, sk):
    d, p, q = sk
    n = p * q

    s = mod_gorner(m, d, n)
    print(f"Sign: {s}")

    return s

def Verify_nohash(packet, pk):
    m, s = packet
    n, e = pk

    recovered_m = mod_gorner(s, e, n)
    if (recovered_m == m):
        print("Повідомлення і підпис співпадають")
    else:
        print("Повідомлення і підпис не співпадають")
    return recovered_m == m

def SendKey_nohash(sk_A, pk_A, pk_B):
    nA, _ = pk_A
    nB, _ = pk_B

    while nB<nA:
        print("Перегенерація пари ключів відправника для коректної роботи протоколу конфіденційного розсилання ключів\n")
        small_primes = GenSmallPrimes()
        n0 = 1 << 255
        n1 = (1 << 256) - 1
        p3  = RandPrime(small_primes, n0, n1)
        q3  = RandPrime(small_primes, n0, n1)
        nA = p3 * q3
        pk_A, sk_A = GenKeyPair(p3, q3)

    k = random.randrange(1, nA-1)
    print(f"Created key: {k}")

    k1, _ = Encrypt(k, pk_B)
    s = Sign_nohash(k, sk_A)
    s1, _ = Encrypt(s, pk_B)

    return (k1, s1), k, pk_A, sk_A            

def RecvKey_nohash(packet, sk_B, pk_A):
    k1,s1 = packet

    k = Decrypt(k1, sk_B, m_type="int")
    s = Decrypt(s1, sk_B, m_type="int")

    packet = (k, s)
    verified = Verify_nohash(packet, pk_A)

    if verified:
        return k
    else:
        return "message compromised"
    
def main():
    # Test
    # pk_server
    n_s_hex = "9ED649B66A1845081B7AB323900688BAE2502DF15D2AEAEA9E39E24D053815AD"
    e_s_hex = "10001"
    print("\n", "-"*100, "\n")
    print("SERVER\n")
    print(f"n_s hex: {n_s_hex} \ne_s hex: {e_s_hex}\n")
    n_s = int(n_s_hex, 16)
    e_s = int(e_s_hex, 16)
    print(f"n_s: {n_s} \ne_s: {e_s}")
    print("\n", "-"*100, "\n")
    pk_s = (n_s, e_s)

    # В якості клієнта будемо використовувати абонента С з pk_С, sk_С
    print("CLIENT\n")
    # Для фіксованого значення, обрав p, q, згенеровані gen_primes_128_256bit.py
    p_C = 89952803302743973242684820091100452396769521585510083744087843288083864385013
    q_C = 113185952448982343257461846858511666938310140333639326275953780654565069484579
    small_primes = GenSmallPrimes()
    if miller_rabin_test(p_C, 15, small_primes):
        print("q_C просте")
    if miller_rabin_test(q_C, 15, small_primes):
        print("p_C просте")
    
    pk_C, sk_C = GenKeyPair(p_C, q_C)
    n_C, e_C = pk_C

    print(f"n_C: {n_C} \ne_C: {e_C}\n")
    n_C_hex = hex(n_C)[2:].upper()
    e_C_hex = hex(e_C)[2:].upper()
    print(f"n_C hex: {n_C_hex} \ne_C hex: {e_C_hex}")
    print("\n", "-"*100, "\n")

    print("ШИФРУВАННЯ")
    msg = 125556937
    msg_hex = hex(msg)[2:].upper()
    print(f"msg hex: {msg_hex}")
    enc, _ = Encrypt(msg, pk_s)
    enc_hex = hex(enc)[2:].upper()
    print(f"Encrypted hex: {enc_hex}")

    print("\nДЕШИФРУВАННЯ")
    ciph_hex = "5D027A8CB9FDBE4CC6DD97DB47F1CB86F3C2CB8DB569F714B020DF79B20B8E6C2C4BE2C8F9830642C6E46C30B5DFD28A37B084FA562A553E971BAB0A7DBED0F0"
    ciph =int(ciph_hex, 16)
    print(f"Cipher hex: {ciph_hex}\nCipher: {ciph}")
    dec = Decrypt(ciph, sk_C, m_type=None)

    print("\nПЕРЕВІРКА ПІДПИСУ")
    sign_s_hex = "34C616A3CDCDC0A7AB4A924050FE2772A2BA92D0244EDF2A6725FB2FF740BA5D"
    msg_s_hex = "1234F"
    print(f"Sign hex: {sign_s_hex}\nmsg hex: {msg_s_hex}")
    sign_s = int(sign_s_hex, 16)
    msg_s = int(msg_s_hex, 16)
    print(f"Sign: {sign_s}\msg: {msg_s}")
    verified = Verify_nohash((msg_s, sign_s), pk_s)
    if verified:
        print(f"Повідомлення hex: {hex(msg_s)[2:].upper()}")

    print("\nПІДПИС")
    s = Sign_nohash(msg, sk_C)
    s_hex = hex(s)[2:].upper()
    msg_hex = hex(msg)[2:].upper()
    print(f"msg: {msg}")
    print(f"msg hex: {msg_hex}\nSign hex: {s_hex}")

    print("\nОТРИМАТИ КЛЮЧ")
    k1_hex = "B4E8DD8A83359E474DBBCD14A61D126FAC38AAC090711664BEBF45A68BF4310C4CE5AB1DE699CF45CEE8B918C387FA5FDFC8B26A89B54CBBF9805FE9ED16A2A1"
    s1_hex = "04F72A65529C29281B5B80B1E647D00592DFF333D10EBAEF7133DB66165BBD643428BF186F12FBAF27EC6E31AFBC3DC79A6ACF5CEC3936DBF39972CF3EFC3B36"
    print(f"k1 hex: {k1_hex}")
    print(f"s1 hex: {s1_hex}")   
    s1 = int(s1_hex, 16)
    k1 = int(k1_hex, 16)
    k = RecvKey_nohash((k1, s1), sk_C, pk_s)
    print(f"Отримано ключ {k}")

    # для цього нам не підходять прості числа довжини 256, тому спробуємо 128
    print("\nВІДПРАВИТИ КЛЮЧ")
    pD = 253942280408410956467570022732184930511
    qD = 188392119911846272681768014465358438541
    pk_D, sk_D = GenKeyPair(pD, qD)
    n_D, e_D = pk_D

    print(f"n_D: {n_D} \ne_D: {e_D}\n")
    n_D_hex = hex(n_D)[2:].upper()
    e_D_hex = hex(e_D)[2:].upper()
    print(f"n_D hex: {n_D_hex} \ne_D hex: {e_D_hex}\n")
    packet, k1, pk_D, sk_D = SendKey_nohash(sk_D, pk_D, pk_s)
    print(f"Saved key: {k1}")
    kc, sc = packet
    kc_hex = hex(kc)[2:].upper()
    sc_hex = hex(sc)[2:].upper()
    print(f"key hex: {kc_hex}\nsign hex: {sc_hex}")

    
if __name__ == "__main__":
    main()