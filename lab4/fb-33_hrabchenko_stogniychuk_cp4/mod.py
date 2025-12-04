# Розширений алгоритм Евкліда
def gcd_extended(a, b):
    if a == 0:
        return b, 0, 1
    
    gcd, x1, y1 = gcd_extended(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def gcd(a, b):
    if a == 0:
        return b
    
    d = gcd(b % a, a)
    return d

# Обчислення оберненого за модулем числа з використанням розширеного алгоритму Евкліда
def mod_inverse(a, mod):
    gcd, x, _ = gcd_extended(a, mod)
    if gcd != 1:
        raise ValueError(f"Обернене число не існує для a = {a} і mod = {mod}.")
    
    return x % mod

# Розв'язання лінійних конгруенцій у вигляді ax ≡ b (mod m)
def linear_congruence(a, b, mod):
    gcd, x, _ = gcd_extended(a, mod)
    if b % gcd != 0:
        raise ValueError(f"Розв'язок не існує для рівняння {a}x ≡ {b} (mod {mod}).")
    
    # Нормалізація рівняння
    a, b, mod = a // gcd, b // gcd, mod // gcd
    x0 = (mod_inverse(a, mod) * b) % mod  # Частковий розв'язок

    # Генерація всіх розв'язків
    result = [(x0 + i * mod) % (mod * gcd) for i in range(gcd)]
    return result

def test_mod_inverse():
    print("\n=== Тестування оберненого за модулем числа ===")
    
    # Тест 1: Простий випадок, де обернене існує
    try:
        a, mod = 3, 26
        inv = mod_inverse(a, mod)
        print(f"Тест 1: Обернене число для {a} mod {mod} = {inv}")
        print(f"Перевірка: {a} * {inv} mod {mod} = {(a * inv) % mod}")
    except ValueError as e:
        print(f"Тест 1 не пройдено: {e}")

    # Тест 2: Обернене не існує (a і mod не взаємно прості)
    try:
        a, mod = 4, 8
        inv = mod_inverse(a, mod)
        print(f"Тест 2: Обернене число для {a} mod {mod} = {inv}")
    except ValueError as e:
        print(f"Тест 2 (очікувана помилка): {e}")

    # Тест 3: Великі числа
    try:
        a, mod = 123, 4567
        inv = mod_inverse(a, mod)
        print(f"Тест 3: Обернене число для {a} mod {mod} = {inv}")
        print(f"Перевірка: {a} * {inv} mod {mod} = {(a * inv) % mod}")
    except ValueError as e:
        print(f"Тест 3 не пройдено: {e}")

def Horner(x, e, mod):
    """
    Швидке піднесення до степеня(e) за модулем за схемою Горнера.
    """
    y = 1
    e_bits = bin(e)[2:]  
    for bit in e_bits:
        y = (y * y) % mod  
        if bit == '1':
            y = (y * x) % mod  
    return y


def test_linear_congruence():
    print("\n=== Тестування лінійних конгруенцій ===")
    
    # Тест 1: Єдиний розв'язок
    try:
        a, b, mod = 3, 4, 7
        solutions = linear_congruence(a, b, mod)
        print(f"Тест 1: Розв'язки рівняння {a}x ≡ {b} (mod {mod}): {solutions}")
        for x in solutions:
            print(f"Перевірка: {a} * {x} mod {mod} = {(a * x) % mod}")
    except ValueError as e:
        print(f"Тест 1 не пройдено: {e}")

    # Тест 2: Кілька розв'язків
    try:
        a, b, mod = 6, 4, 10
        solutions = linear_congruence(a, b, mod)
        print(f"Тест 2: Розв'язки рівняння {a}x ≡ {b} (mod {mod}): {solutions}")
        for x in solutions:
            print(f"Перевірка: {a} * {x} mod {mod} = {(a * x) % mod}")
    except ValueError as e:
        print(f"Тест 2 не пройдено: {e}")

    # Тест 3: Немає розв'язків
    try:
        a, b, mod = 4, 3, 6
        solutions = linear_congruence(a, b, mod)
        print(f"Тест 3: Розв'язки рівняння {a}x ≡ {b} (mod {mod}): {solutions}")
    except ValueError as e:
        print(f"Тест 3 (очікувана помилка): {e}")

    # Тест 4: Великі числа з кількома розв'язками
    try:
        a, b, mod = 14, 30, 100
        solutions = linear_congruence(a, b, mod)
        print(f"Тест 4: Розв'язки рівняння {a}x ≡ {b} (mod {mod}): {solutions}")
        for x in solutions:
            print(f"Перевірка: {a} * {x} mod {mod} = {(a * x) % mod}")
    except ValueError as e:
        print(f"Тест 4 не пройдено: {e}")

if __name__ == "__main__":
    test_mod_inverse()
    test_linear_congruence()
