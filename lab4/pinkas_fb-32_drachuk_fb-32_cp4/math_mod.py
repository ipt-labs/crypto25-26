# This script has no specific requirements
def gcd(a, b):
    while b > 0:
        # q = a // b
        r = a % b
        a, b = b, r
    return a

def find_inverse_element(a, m):
    # r=a*u+m*v, u - коефіцієнт біля a, v - коефіцієнт біля m
    u0, u1 = 0, 1 
    v0, v1 = 1, 0

    m_init = m # зберігаємо значення модуля перед перевизначенням в операціях
    while a > 0:
        q = m // a # 13/5 = 2
        r = m % a # 13 - 2 * 5 = 3
        # -> 13 = 2 * 5 + 3

        m, a = a, r # 5, 2 (наступний крок, зносимо a і r)

        next_u0 = u1
        next_v0 = v1
        # 3 = (13*0 + 5*1) - 2*(13*1 + 5*0)
        u1= u0 - q * u1 #0 -2*1 = -2, коеф. біля a
        v1 = v0 - q* v1 # 1-2*0 = 1, коеф. біля m
        # 3 = -2 * 5 + 1 * 13

        # оновлюємо початкові коефіцієнти для наступного кроку
        u0, v0 = next_u0, next_v0

    if m != 1:
        return None
    else:
        return u0 % m_init # повертаємо коеф. біля a за модулем m (u0, тому що останній крок 0 = u*0 +v*m, а треба 1=ua+vm)

def mod_gorner(a, n, m): # (a^n) modm
    b = 1
    highest_bit = n.bit_length() - 1
    a = a % m

    for i in range(highest_bit, -1, -1): # k-1 to 0
        b = (b**2) % m

        if (n >> i) & 1:
            b = (b * a) % m # домножуємо на a, якщо біт - 1

    return b