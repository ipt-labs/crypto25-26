from typing import Optional
from helpers.modular_arithmetic import modular_inverse


class BigramAffineCipher:
    def __init__(self, alphabet:str):
        if not alphabet:
            raise ValueError("alphabet should be provided")
        self.alphabet = alphabet
        self.char_to_idx = {ch: i for i, ch in enumerate(alphabet)}
        self.alphabet_len = len(alphabet)
        self.idx_to_bigram = {self.bigram_to_int(c1+c2):c1+c2 for c1 in alphabet for c2 in alphabet}
        self.modulus = self.alphabet_len**2
    
    def bigram_to_int(self, bigram:str)->Optional[int]:
        if len(bigram) != 2:
            return None
        return self.char_to_idx[bigram[0]]*self.alphabet_len+self.char_to_idx[bigram[1]]
    
    def decrypt(self, ct: str, a: int, b: int) -> str:
        res = ""
        if len(ct) < 2:
            raise ValueError("text should have at least 2 chars")
        a_inv = modular_inverse(a, self.modulus)
        if a_inv is None:
            raise ValueError(f"can not decrypt with key ({a},{b}) because inverse mod {self.modulus} does not exist for {a}")
        for i in range(0, len(ct)-1, 2):
            c1 = ct[i]
            c2 = ct[i+1]
            if c1 not in self.alphabet or c2 not in self.alphabet:
                raise ValueError("ct contains values not from alphabet")
            res += self.idx_to_bigram[(a_inv * (self.bigram_to_int(c1 + c2) - b)) % self.modulus]
        return res