'''
Частина 1: Математичні примітиви
'''

# Розширений алгоритм Евкліда.
def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    else:
        g, y, x = extended_gcd(b % a, a)
        return g, x - (b // a) * y, y

# Знаходить обернений елемент a^(-1) за модулем m.
def mod_inverse(a, m):
    g, x, y = extended_gcd(a, m)
    if g != 1:
        return None
    else:
        return x % m

# Розв'язує лінійне порівняння: ax ≡ b (mod n).
def solve_linear_congruence(a, b, n):
    g, x, y = extended_gcd(a, n)

    if b % g != 0:
        return []

    # a/g * x ≡ b/g (mod n/g)
    x0 = (x * (b // g)) % n

    solutions = []
    step = n // g
    for k in range(g):
        solutions.append((x0 + k * step) % n)

    return solutions

# Перевірка роботи 1 завдання
print("\n--- Перевірка 1 завдання ---")
try:
    # Тест 1: Обернений елемент
    a = 3
    m = 11
    inv = mod_inverse(a, m)

    print(f"Обернений елемент до {a} по модулю {m} = {inv}")

    # Тест 2: Лінійне порівняння з декількома розв'язками
    a, b, n = 2, 4, 6
    sols = solve_linear_congruence(a, b, n)

    print(f"Розв'язки порівняння {a}x ≡ {b} (mod {n}): {sols}")

except Exception as e:
    print(f"ПОМИЛКА Завдання 1: {e}")
