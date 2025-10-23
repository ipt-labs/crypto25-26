from typing import List


def modular_inverse(a:int, m:int)->int:    
    start_m = m
    u_0 = 1
    u_1 = 0
    
    while a>1:
        q = a // m
        a, m = m, a % m
        u_0, u_1 = u_1, u_0 - q * u_1

    if (u_0 < 0):
        u_0 += start_m

    return u_0


def gcd(a:int,b:int)->int:
    while b:
        a,b = b, a%b
    return a


def modular_linear_equation(a:int,b:int,m:int)->List[int]:
    a_m_gcd = gcd(a,m)
    if (a_m_gcd==1):
        return [(b*modular_inverse(a,m)) % m]
    elif (b%a_m_gcd!=0):
        return []
    else:
        a_1 = a // a_m_gcd
        b_1 = b // a_m_gcd
        m_1 = m // a_m_gcd
        x_0 = (b_1*modular_inverse(a_1,m_1)) % m_1
        return [x_0+m_1*i for i in range(a_m_gcd)]