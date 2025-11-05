def gcd(a, b):
    if b == 0:
        return a, 1, 0
    g, x1, y1 = gcd(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    return g, x, y

def inverse(a, m):
    g, x, _ = gcd(a, m)
    if g != 1:
        return None
    return x % m

def solve(a, b, m):
    g, x, y = gcd(a, m)
    if b % g != 0:
        return []
    a1 = a // g
    b1 = b // g
    m1 = m // g

    inv = inverse(a1, m1)
    if inv is None:
        return []

    x0 = (inv * b1) % m1
    result = []
    for i in range(g):
        result.append(x0 + i * m1)
    return result

print("Приклад 1:")
a = 3
m = 11
inv_el = inverse(a, m)
if inv_el is None:
    print(f"Оберненого елементу для {a} за модулем {m} не існує.")
else:
    print(f"Обернений елемент для {a} за модулем {m}: {inv_el}")

print("\nПриклад 2:")
a = 10
m = 17
inv_el = inverse(a, m)
if inv_el is None:
    print(f"Оберненого елементу для {a} за модулем {m} не існує.")
else:
    print(f"Обернений елемент для {a} за модулем {m}: {inv_el}")

print("\nПриклад 3:")
a = 6
m = 15
inv_el = inverse(a, m)
if inv_el is None:
    print(f"Оберненого елементу для {a} за модулем {m} не існує.")
else:
    print(f"Обернений елемент для {a} за модулем {m}: {inv_el}")

print("\nПриклад 4:")
a = 6
b = 18
m = 24
result = solve(a, b, m)
if not result:
    print(f"Для {a}x ≡ {b} (mod {m}) немає розв'язків.")
else:
    print(f"Розв'язки для {a}x ≡ {b} (mod {m}): {result}")

print("\nПриклад 5:")
a = 7
b = 5
m = 13
result = solve(a, b, m)
if not result:
    print(f"Для {a}x ≡ {b} (mod {m}) немає розв'язків.")
else:
    print(f"Розв'язок для {a}x ≡ {b} (mod {m}): {result}")

print("\nПриклад 6:")
a = 6
b = 5
m = 12
result = solve(a, b, m)
if not result:
    print(f"Для {a}x ≡ {b} (mod {m}) немає розв'язків.")
else:
    print(f"Розв'язок для {a}x ≡ {b} (mod {m}): {result}")
