from random_prime import generate_prime_pairs
from mod import gcd, mod_inverse 

def generate_rsa_keys(p, q):
    """
    Генерує пару ключів RSA для заданих простих чисел p і q.
    Повертає:
      - Відкритий ключ (n, e)
      - Секретний ключ (d, p, q)
    """
    n = p * q
    phi = (p - 1) * (q - 1)

    e = 65537  
    if gcd(e, phi) != 1:
        raise ValueError("Не вдалося обрати e взаємно просте з phi(n)")

    d = mod_inverse(e, phi)
    return (n, e), (d, p, q)


if __name__ == "__main__":
    bit_length = 256

    (p, q, _, _), (p1, q1, _, _) = generate_prime_pairs(bit_length)

    # Генеруємо ключі для абонента А
    public_a, private_a = generate_rsa_keys(p, q)
    n_a, e_a = public_a
    d_a, p_a, q_a = private_a

    # Генеруємо ключі для абонента B
    public_b, private_b = generate_rsa_keys(p1, q1)
    n_b, e_b = public_b
    d_b, p_b, q_b = private_b

    print("=" * 160)
    print("Ключі абонента A:")
    print("-" * 160)
    print(f"Відкритий ключ:\n  e = {e_a}\n  n = {n_a}")
    print("-" * 160)
    print(f"Секретний ключ:\n  d = {d_a}\n  p = {p_a}\n  q = {q_a}")
    print("=" * 160)

    print("Ключі абонента B:")
    print("-" * 160)
    print(f"Відкритий ключ:\n  e = {e_b}\n  n = {n_b}")
    print("-" * 160)
    print(f"Секретний ключ:\n  d = {d_b}\n  p = {p_b}\n  q = {q_b}")
    print("=" * 160)
