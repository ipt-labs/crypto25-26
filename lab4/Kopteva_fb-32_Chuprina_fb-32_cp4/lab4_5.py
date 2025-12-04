import random
from typing import Tuple, Union
from lab4_123 import generate_and_check_primes, BIT_LENGTH
from lab4_4 import Encrypt, Decrypt, Sign, Verify

def SendKey(K: int, d_A: int, e_B: int, n_A: int, n_B: int) -> Tuple[int, int]:
    C = Encrypt(K, e_B, n_B)
    S = Sign(K, d_A, n_A)

    return C, S


def ReceiveKey(C: int, S: int, d_B: int, e_A: int, n_A: int, n_B: int) -> Union[Tuple[bool, int], Tuple[bool, None]]:
    K_decrypted = Decrypt(C, d_B, n_B)
    is_verified = Verify(K_decrypted, S, e_A, n_A)

    if is_verified:
        return True, K_decrypted
    else:
        return False, None


if __name__ == '__main__':
    keys_A, keys_B = generate_and_check_primes()
    n_min = min(keys_A.n, keys_B.n)
    K_session = random.getrandbits(BIT_LENGTH) % n_min

    print("\n--- Протокол конфіденційного розсилання ключів (Завдання 5) ---")
    print(f"Оригінальний сеансовий ключ K: {K_session}")

    print("\n[АБОНЕНТ А (Відправник)]")
    C_key, S_key = SendKey(
        K_session,
        keys_A.d, keys_B.e, 
        keys_A.n, keys_B.n
    )
    print(f"  Надсилає C (шифрований K): {C_key}")
    print(f"  Надсилає S (підписаний K): {S_key}")
    print("\n[АБОНЕНТ В (Отримувач)]")

    is_protocol_ok, K_received = ReceiveKey(
        C_key, S_key,
        keys_B.d, keys_A.e, 
        keys_A.n, keys_B.n
    )
    print(f"  Результат перевірки справжності: {is_protocol_ok}")

    if is_protocol_ok and K_received is not None:
        print(f"  Отриманий ключ K: {K_received}")
        print(f"  ПЕРЕВІРКА КЛЮЧІВ: {K_session == K_received}")
    else:
        print("  ПОМИЛКА: Протокол завершено невдачею. Підпис недійсний.")
