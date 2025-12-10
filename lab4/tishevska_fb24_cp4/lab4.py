import random


RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

CYAN = "\033[36m"
YELLOW = "\033[33m"
GREEN = "\033[32m"
MAGENTA = "\033[35m"
BLUE = "\033[34m"
RED = "\033[31m"

def section(title):
    line = "─" * (len(title) + 2)
    print(f"\n{MAGENTA}┌{line}┐{RESET}")
    print(f"{MAGENTA}│ {BOLD}{title}{RESET}{MAGENTA} │{RESET}")
    print(f"{MAGENTA}└{line}┘{RESET}\n")

def subheader(title):
    print(f"{CYAN}{BOLD}▶ {title}{RESET}")

def kv(label, value, indent=2):
    pad = " " * indent
    print(f"{pad}{YELLOW}{label}{RESET} {value}")


log = []


def ext_gcd(a, b):
    if a == 0:
        return b, 0, 1
    else:
        gcd, x, y = ext_gcd(b % a, a)
        return gcd, y - (b // a) * x, x


def modInverse(num, mod):
    a, b = num, mod
    x, y, u, v = 0, 1, 1, 0
    while a != 0:
        q, r = divmod(b, a)
        m, n = x - u * q, y - v * q
        b, a, x, y, u, v = a, r, u, v, m, n
    return x % mod


def miller_rabin(p):
    d = p - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2

    for _ in range(10):
        x = random.randint(1, p - 1)
        pw = pow(x, d, p)
        if pw == 1 or pw == p - 1:
            continue

        for _ in range(1, s):
            pw = pow(pw, 2, p)
            if pw == p - 1:
                break
        else:
            return False

    return True


def find_primes():
    prime = random.getrandbits(256)
    if prime % 2 == 0:
        prime += 1
    while not miller_rabin(prime):
        log.append(prime)
        prime += 2

    return prime


def gen_pairs():
    p, q, p1, q1 = 0, 0, 0, 0
    while True:
        p = find_primes()
        q = find_primes()
        p1 = find_primes()
        q1 = find_primes()
        if p * q <= p1 * q1:
            break
    return p, q, p1, q1


def gen_rsa_keys(p, q):
    n = p * q
    oiler = (p - 1) * (q - 1)

    while True:
        e = random.randint(2, oiler - 1)
        if ext_gcd(e, oiler)[0] == 1:
            d = modInverse(e, oiler)
            break

    return (e, n), (d, p, q)


def encrypt(M, e, n):
    return pow(M, e, n)


def decrypt(C, d, n):
    return pow(C, d, n)


def sign(M, Sec_key):
    S = pow(M, Sec_key[0], Sec_key[1] * Sec_key[2])
    return S


def verify(M, S, Pub_key):
    return M == pow(S, Pub_key[0], Pub_key[1])


def send_key(k, Sec_key, Pub_B):
    k1 = encrypt(k, Pub_B[0], Pub_B[1])
    S = sign(k, Sec_key)
    S1 = encrypt(S, Pub_B[0], Pub_B[1])

    section("ВІДПРАВКА КЛЮЧА (A → B)")
    subheader("Дані, які надсилає A")
    kv("k1 (k, зашифрований ключем B):", k1)
    kv("S  (підпис k приватним ключем A):", S)
    kv("S1 (S, зашифрований ключем B):", S1)

    return (k1, S1)


def recieve_key(msg, Sec_key, Pub_A):
    k = decrypt(msg[0], Sec_key[0], Sec_key[1] * Sec_key[2])
    S = decrypt(msg[1], Sec_key[0], Sec_key[1] * Sec_key[2])
    check = verify(k, S, Pub_A)

    section("ОТРИМАННЯ КЛЮЧА (B)")
    subheader("Результат обробки повідомлення B")
    kv("k (розшифрований ключ):", k)
    kv("S (розшифрований підпис):", S)
    kv("Перевірка підпису:", f"{GREEN}OK{RESET}" if check else f"{RED}FAIL{RESET}")

    return (k, check)


if __name__ == '__main__':
    section("ГЕНЕРАЦІЯ ПАР ПРАЙМІВ ДЛЯ RSA")
    p, q, p1, q1 = gen_pairs()

    section("ГЕНЕРАЦІЯ КЛЮЧІВ RSA")
    Pub_A, Sec_A = gen_rsa_keys(p, q)
    Pub_B, Sec_B = gen_rsa_keys(p1, q1)

    subheader("Ключі абонента A")
    kv("Відкритий ключ A (e, n):", "")
    kv("eA =", Pub_A[0], 6)
    kv("nA =", Pub_A[1], 6)
    kv("Секретний ключ A (d, p, q):", "")
    kv("dA =", Sec_A[0], 6)
    kv("pA =", Sec_A[1], 6)
    kv("qA =", Sec_A[2], 6)

    print()
    subheader("Ключі абонента B")
    kv("Відкритий ключ B (e, n):", "")
    kv("eB =", Pub_B[0], 6)
    kv("nB =", Pub_B[1], 6)
    kv("Секретний ключ B (d, p, q):", "")
    kv("dB =", Sec_B[0], 6)
    kv("pB =", Sec_B[1], 6)
    kv("qB =", Sec_B[2], 6)

    print()
    subheader("Кандидати в прості, що не пройшли тест Міллера–Рабіна")
    kv("Кількість:", len(log))
    kv("Перші 10:", log[:10])

    
    section("ДЕМОНСТРАЦІЯ RSA: ШИФРУВАННЯ / РОЗШИФРУВАННЯ")
    M = 4561119
    kv("Вихідний текст M:", M)
    C = encrypt(M, Pub_A[0], Pub_A[1])
    kv("Шифртекст C = M^e mod n:", C)
    M_dec = decrypt(C, Sec_A[0], Pub_A[1])
    kv("Розшифрований текст M' =", M_dec)
    print()

    subheader("Цифровий підпис A")
    signed = sign(M_dec, Sec_A)
    kv("Підпис S = M'^d mod n:", signed)
    kv("Перевірка підпису verify(M', S, Pub_A):",
       f"{GREEN}{verify(M_dec, signed, Pub_A)}{RESET}")

    # ====== ДЕМО: Обмін ключем ======
    section("ФОРМУВАННЯ ВИПАДКОВОГО СЕАНСОВОГО КЛЮЧА")
    k = random.randint(0, Pub_A[1])
    kv("Сеансовий ключ k:", k)

    msg = send_key(k, Sec_A, Pub_B)
    kv("Пара (k1, S1), що реально йде по каналу:", msg)

    recieved = recieve_key(msg, Sec_B, Pub_A)
    kv("Отриманий ключ та результат перевірки:", recieved)

    print(f"\n{MAGENTA}{'─' * 50}{RESET}\n")

    # ====== ДОДАТКОВІ ПРИКЛАДИ З ФІКСОВАНИМИ ПАРАМЕТРАМИ ======
    section("ДОДАТКОВІ ПРИКЛАДИ З ФІКСОВАНИМИ ПАРАМЕТРАМИ")
    M = 4561119
    subheader("Приклад 1: шифрування для великого модуля m")
    kv("M (десяткове):", M)
    kv("M (hex):", hex(M))

    m = 5305960512707629841442515833661084058562762878355119201853129312962340025770214010720538446853744323527655052091932568360456540587057370566022074996520867
    e = 3916586186136903342915117154323316045631285621401634288542736693723028692209679594314837428255383879983135058969049129222249031314517667534786111118003965
    kv("m:", hex(m), 4)
    kv("e:", hex(e), 4)
    kv("C = M^e mod m:", hex(encrypt(M, e, m)), 4)

    print(f"\n{BLUE}{'-' * 40}{RESET}\n")

    # ====== ТУТ ВИКОРИСТОВУЄМО TVІЙ SERVER KEY ======
    subheader("Приклад 2: використання server key (256 біт)")

    server_mod_hex = "90829D6CAF6C2D76F691E6DC30FC86B8BAD615F148A6C6EF202573A70005FB5D"
    server_e_hex = "10001"  # це 0x10001 = 65537

    server_m = int(server_mod_hex, 16)
    server_e = int(server_e_hex, 16)

    kv("Server key size:", "256 біт", 4)
    kv("Server modulus (hex):", "0x" + server_mod_hex, 4)
    kv("Server public exponent (hex):", "0x" + server_e_hex, 4)

    kv("C = M^e mod server_m:", hex(encrypt(M, server_e, server_m)), 4)

    print(f"\n{BLUE}{'-' * 40}{RESET}\n")

    subheader("Приклад 3: перевірка підпису")
    M = 1938572304
    S = 2935231723390141546401135832555754721151535406204611218226675084725685207703
    kv("M:", hex(M), 4)
    kv("S:", hex(S), 4)
    kv("Verify(M, S, (server_e, server_m)):", verify(M, S, (server_e, server_m)), 4)

    print(f"\n{BLUE}{'-' * 40}{RESET}\n")

    subheader("Приклад 4: підпис із заданими ключами")
    M = 93217509358
    kv("M:", hex(M), 4)
    sec_key = (
        329505922172195841115746731553923783053678201718895159417570805638393840637750743927520556451098736334932075404857751203394250089977717048523234122387429,
        40579744356376223807099927945683212405087196913505853242083573676362283328141,
        28633471310308254319831997550533605289978359050092793232916603261249542134329
    )
    pub_key = (
        968738930756157653593740847055873301390678725793902309393311372256032228229160736505294459230578934731311734961006551135090117119181232722532481230767789,
        1161938945807941901442265855219021587743836625195666738881218866797062824626719645259205076783721663340363092805469023189319126755883138946141118607852389
    )
    S = sign(M, sec_key)
    kv("m публічного ключа:", hex(pub_key[1]), 4)
    kv("e публічного ключа:", hex(pub_key[0]), 4)
    kv("Підпис S = M^d mod (p*q):", hex(S), 4)

    print(f"\n{GREEN}{BOLD}✔ Роботу завершено успішно.{RESET}\n")
