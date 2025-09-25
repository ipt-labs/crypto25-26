class VigenereCipher:
    def __init__(self, key: str, alphabet: str):
        if not alphabet:
            raise ValueError("alphabet cannot be empty")
        elif not key:
            raise ValueError("key cannot be empty")
        self.alphabet = "".join(dict.fromkeys(alphabet))
        for key_ch in key:
            if key_ch not in self.alphabet:
                raise ValueError("key cannot contain characters that are not in alphabet")
        self.alphabet_len = len(self.alphabet)
        self.key = key
        self.key_len = len(key)
        self.char_to_idx = {ch: i for i, ch in enumerate(self.alphabet)}

    def encrypt(self, pt: str) -> str:
        ct = ""
        for i, ch in enumerate(pt):
            if ch in self.alphabet:
                ct += self.alphabet[
                    (self.char_to_idx[ch] + self.char_to_idx[self.key[i%self.key_len]]) % self.alphabet_len
                ]
        return ct

    def decrypt(self, ct: str) -> str:
        pt = ""
        for i, ch in enumerate(ct):
            if ch in self.alphabet:
                pt += self.alphabet[
                    (self.char_to_idx[ch] - self.char_to_idx[self.key[i%self.key_len]]) % self.alphabet_len
                ]
        return pt


if __name__ == "__main__":
    print("lab2")
    alphabet = "абвгдежзийклмнопрстуфхцчшщыьэюя"