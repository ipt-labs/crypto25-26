"""
Модуль базових арифметичних операцій для RSA криптосистеми
Варіант 6
"""

def fast_power_mod(base: int, exponent: int, modulus: int) -> int:
    """
    Швидке піднесення до степеня за модулем за схемою Горнера
    
    Args:
        base: основа
        exponent: показник степеня
        modulus: модуль
    
    Returns:
        result: base^exponent mod modulus
    """
    result = 1
    base = base % modulus
    
    while exponent > 0:
        if exponent & 1:
            result = (result * base) % modulus
        exponent >>= 1
        base = (base * base) % modulus
    
    return result


def find_gcd(num1: int, num2: int) -> int:
    """
    Алгоритм Евкліда для знаходження НСД
    
    Args:
        num1, num2: числа для знаходження НСД
    
    Returns:
        НСД(num1, num2)
    """
    while num2 != 0:
        num1, num2 = num2, num1 % num2
    return num1


def extended_gcd(num1: int, num2: int) -> tuple[int, int, int]:
    """
    Розширений алгоритм Евкліда
    
    Returns:
        (gcd, x, y) де gcd = num1*x + num2*y
    """
    if num2 == 0:
        return num1, 1, 0
    
    gcd_val, x1, y1 = extended_gcd(num2, num1 % num2)
    x = y1
    y = x1 - (num1 // num2) * y1
    
    return gcd_val, x, y


def compute_mod_inverse(element: int, modulus: int) -> int:
    """
    Знаходження модульного оберненого елемента
    
    Args:
        element: елемент для якого шукаємо обернений
        modulus: модуль
    
    Returns:
        inverse: element^(-1) mod modulus
    
    Raises:
        ValueError: якщо обернений елемент не існує
    """
    gcd_val, x, _ = extended_gcd(element, modulus)
    
    if gcd_val != 1:
        raise ValueError(f"Обернений елемент не існує: gcd({element}, {modulus}) = {gcd_val}")
    
    return (x % modulus + modulus) % modulus
