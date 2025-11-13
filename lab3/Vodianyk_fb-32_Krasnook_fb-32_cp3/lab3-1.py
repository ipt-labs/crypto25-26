import sys
from typing import List, Tuple, Optional

ALPHABET = "абвгдежзийклмнопрстуфхцчшщыьэюя"
M = len(ALPHABET)
M_SQUARED = M * M

print(f"--- Налаштування ---")
print(f"Алфавіт (m = {M} символів): {ALPHABET}")
print(f"Модуль (m^2): {M_SQUARED} (тобто {M}*{M})")

def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    if a == 0:
        return (b, 0, 1)
    gcd, u1, v1 = extended_gcd(b % a, a)
    u = v1 - (b // a) * u1
    v = u1
    return (gcd, u, v)

def mod_inverse(a: int, n: int) -> Optional[int]:
    gcd, u, v = extended_gcd(a, n)
    if gcd != 1:
        return None
    else:
        return u % n

def solve_linear_congruence(a: int, b: int, n: int) -> List[int]:
    a = a % n
    b = b % n
    d, u, v = extended_gcd(a, n)
    solutions = []
    if b % d != 0:
        return []
    a1 = a // d
    b1 = b // d
    n1 = n // d
    a1_inv = mod_inverse(a1, n1)
    if a1_inv is None:
        print("Помилка: неможливо знайти обернений елемент для a1.", file=sys.stderr)
        return []
    x0 = (b1 * a1_inv) % n1
    for i in range(d):
        solutions.append(x0 + i * n1)
    return solutions

print("\n--- Тестування математичного ядра ---")

a_test_1 = 5
n_test = M_SQUARED
inv_1 = mod_inverse(a_test_1, n_test)
print(f"1. Обернений до {a_test_1} mod {n_test} = {inv_1}")
if inv_1 is not None:
    print(f" Перевірка: ({a_test_1} * {inv_1}) % {n_test} = {(a_test_1 * inv_1) % n_test} (має бути 1)")

a_test_2 = 31
inv_2 = mod_inverse(a_test_2, n_test)
print(f"\n2. Обернений до {a_test_2} mod {n_test} = {inv_2} (має бути None)")

a_test_3 = 5
b_test_3 = 7
sols_3 = solve_linear_congruence(a_test_3, b_test_3, n_test)
print(f"\n3. Розв'язки для {a_test_3}x ≡ {b_test_3} (mod {n_test}): {sols_3}")
if sols_3:
    print(f" Перевірка: ({a_test_3} * {sols_3[0]}) % {n_test} = {(a_test_3 * sols_3[0]) % n_test} (має бути {b_test_3})")

a_test_4 = 31
b_test_4 = 7
sols_4 = solve_linear_congruence(a_test_4, b_test_4, n_test)
print(f"\n4. Розв'язки для {a_test_4}x ≡ {b_test_4} (mod {n_test}): {sols_4} (має бути [])")

a_test_5 = 31
b_test_5 = 62
sols_5 = solve_linear_congruence(a_test_5, b_test_5, n_test)
print(f"\n5. Розв'язки для {a_test_5}x ≡ {b_test_5} (mod {n_test}):")
print(f" Кількість розв'язків: {len(sols_5)} (має бути 31)")
print(f" Перші 5 розв'язків: {sols_5[:5]} (має бути [2, 33, 64, 95, 126])")
if sols_5:
    print(f" Перевірка (перший): ({a_test_5} * {sols_5[0]}) % {n_test} = {(a_test_5 * sols_5[0]) % n_test} (має бути {b_test_5})")
    print(f" Перевірка (останній): ({a_test_5} * {sols_5[-1]}) % {n_test} = {(a_test_5 * sols_5[-1]) % n_test} (має бути {b_test_5})")