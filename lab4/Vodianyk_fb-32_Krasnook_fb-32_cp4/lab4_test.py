import random
import requests
import json
import sys

class CryptoEngine:
    @staticmethod
    def _is_prime_mr(n, k=40):
        if n == 2 or n == 3: return True
        if n % 2 == 0 or n < 2: return False
        d, s = n - 1, 0
        while d % 2 == 0:
            d //= 2
            s += 1
        for _ in range(k):
            a = random.randrange(2, n - 1)
            x = pow(a, d, n)
            if x == 1 or x == n - 1: continue
            for _ in range(s - 1):
                x = pow(x, 2, n)
                if x == n - 1: break
            else: return False
        return True

    @staticmethod
    def get_prime_num(bits):
        while True:
            c = random.getrandbits(bits) | (1 << bits - 1) | 1
            if c % 3 != 0 and c % 5 != 0 and CryptoEngine._is_prime_mr(c):
                return c

    @staticmethod
    def egcd(a, b):
        if a == 0: return b, 0, 1
        g, y, x = CryptoEngine.egcd(b % a, a)
        return g, x - (b // a) * y, y

    @staticmethod
    def mod_inverse(a, m):
        g, x, y = CryptoEngine.egcd(a, m)
        if g != 1: raise ValueError("Inversion error")
        return x % m

    @staticmethod
    def keygen(bits=256):
        p = CryptoEngine.get_prime_num(bits)
        q = CryptoEngine.get_prime_num(bits)
        while p == q: q = CryptoEngine.get_prime_num(bits)
        n = p * q
        phi = (p - 1) * (q - 1)
        e = 65537
        while CryptoEngine.egcd(e, phi)[0] != 1: e = random.randrange(3, phi, 2)
        d = CryptoEngine.mod_inverse(e, phi)
        return {'private': (d, p, q), 'public': (n, e)}

    @staticmethod
    def encrypt(m, pub): return pow(m, pub[1], pub[0])
    @staticmethod
    def decrypt(c, priv): return pow(c, priv[0], priv[1]*priv[2])
    @staticmethod
    def sign(m, priv): return pow(m, priv[0], priv[1]*priv[2])
    @staticmethod
    def verify(m, s, pub): return pow(s, pub[1], pub[0]) == m

class WebTester:
    API_URL = "http://asymcryptwebservice.appspot.com/rsa/"
    
    def __init__(self):
        self.http = requests.Session()
        self.keys = None
        self.server_key = None

    def _to_hex(self, val): return hex(val)[2:].upper()
    
    def _preview(self, val):
        if isinstance(val, int): h = hex(val)[2:].upper()
        else: h = val
        if len(h) > 20: return f"{h[:10]}...{h[-10:]} (Len: {len(h)})"
        return h

    def _txt2int(self, txt): return int.from_bytes(txt.encode(), 'big')
    
    def _int2txt(self, val):
        try: return val.to_bytes((val.bit_length()+7)//8, 'big').decode()
        except: return "<BINARY>"

    def setup(self):
        print("Генерація локальних ключів...")
        self.keys = CryptoEngine.keygen(256)
        n, e = self.keys['public']
        print(f"Ключі згенеровано. Modulus: {self._preview(n)}")

    def get_server_pubkey(self):
        print("Отримання ключа сервера...")
        try:
            r = self.http.get(f"{self.API_URL}serverKey?keySize=512")
            js = r.json()
            n = int(js['modulus'], 16)
            e = int(js['publicExponent'], 16)
            self.server_key = (n, e)
            print(f"Ключ сервера отримано. Modulus: {self._preview(n)}")
        except Exception as e:
            print(f"Помилка з'єднання: {e}")
            sys.exit()

    def test_encryption_flow(self):
        print("\n--- Тест 1: Шифрування (Confidentiality) ---")
        msg = "SecretMessage"
        n, e = self.keys['public']
        params = {
            'modulus': self._to_hex(n), 'publicExponent': self._to_hex(e),
            'message': msg, 'type': 'TEXT'
        }
        
        r = self.http.get(f"{self.API_URL}encrypt", params=params)
        c_hex = r.json()['cipherText']
        print(f"Отримано шифротекст: {self._preview(int(c_hex, 16))}")
        
        m_dec_int = CryptoEngine.decrypt(int(c_hex, 16), self.keys['private'])
        m_dec_txt = self._int2txt(m_dec_int)
        
        if m_dec_txt == msg:
            print(f"Дешифрування успішне: {m_dec_txt}")
        else:
            print(f"Помилка дешифрування. Отримано: {m_dec_txt}")

    def test_signature_flow(self):
        print("\n--- Тест 2: Цифровий підпис (Integrity) ---")
        msg = "SignatureTest"
        m_int = self._txt2int(msg)
        s_loc = CryptoEngine.sign(m_int, self.keys['private'])
        n, e = self.keys['public']
        
        print(f"Локальний підпис: {self._preview(s_loc)}")
        
        params = {
            'message': msg, 'signature': self._to_hex(s_loc),
            'modulus': self._to_hex(n), 'publicExponent': self._to_hex(e),
            'type': 'TEXT'
        }
        r = self.http.get(f"{self.API_URL}verify", params=params)
        
        if r.json().get('verified'):
            print("Сервер підтвердив валідність підпису.")
        else:
            print("Сервер відхилив підпис.")

    def test_tampering(self):
        print("\n--- Тест 3: Спроба злому (Tampering) ---")
        msg = "FakeData"
        m_int = self._txt2int(msg)
        s_loc = CryptoEngine.sign(m_int, self.keys['private'])
        
        fake_sig = s_loc + 1337 
        print(f"Відправляємо ПОШКОДЖЕНИЙ підпис...")
        
        n, e = self.keys['public']
        params = {
            'message': msg, 'signature': self._to_hex(fake_sig),
            'modulus': self._to_hex(n), 'publicExponent': self._to_hex(e),
            'type': 'TEXT'
        }
        r = self.http.get(f"{self.API_URL}verify", params=params)
        
        if not r.json().get('verified'):
            print("УСПІХ: Сервер відхилив підроблений підпис (як і очікувалось).")
        else:
            print("ПРОВАЛ: Сервер прийняв підробку!")

    def test_key_exchange_protocol(self):
        print("\n--- Тест 4: Протокол обміну ключами (SendKey) ---")
        session_k = random.randint(10000, 99999)
        print(f"Згенеровано сесійний ключ k: {session_k}")
        
        k_enc = CryptoEngine.encrypt(session_k, self.server_key)
        k_sig = CryptoEngine.sign(session_k, self.keys['private'])
        sig_enc = CryptoEngine.encrypt(k_sig, self.server_key)
        
        n, e = self.keys['public']
        params = {
            'key': self._to_hex(k_enc),
            'signature': self._to_hex(sig_enc),
            'modulus': self._to_hex(n),
            'publicExponent': self._to_hex(e)
        }
        
        r = self.http.get(f"{self.API_URL}receiveKey", params=params)
        
        try:
            js = r.json()
            print(f"Відповідь сервера (Raw): {js}")
            
            server_k_hex = js.get('key')
            server_k_int = int(server_k_hex, 16)
            
            if server_k_int == session_k:
                 print(f"УСПІХ: Сервер повернув ключ {server_k_int} (співпадає з {session_k})")
            else:
                 print(f"Помилка: {server_k_int} != {session_k}")
                 
        except Exception as e:
            print(f"Неможливо розпарсити відповідь: {r.text}")

    def run(self):
        try:
            self.setup()
            self.get_server_pubkey()
            self.test_encryption_flow()
            self.test_signature_flow()
            self.test_tampering()
            self.test_key_exchange_protocol()
            print("\nВсі тести пройдено успішно.")
        except Exception as e:
            print(f"Критична помилка: {e}")

if __name__ == "__main__":
    app = WebTester()
    app.run()