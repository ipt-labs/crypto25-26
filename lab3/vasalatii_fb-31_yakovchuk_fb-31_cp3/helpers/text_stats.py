import math


class TextStats:
    def __init__(self, alphabet:str):
        if not alphabet:
            raise ValueError("alphabet should be provided")
        self.alphabet = alphabet
        self.alphabet_len = len(self.alphabet)

    def bigram_occurrences(self, text: str) -> dict[str, int]:
        bigram_count = {c1+c2:0 for c1 in self.alphabet for c2 in self.alphabet}
        if len(text) < 2:
            return bigram_count
        for i in range(0, len(text)-1, 2):
            c1 = text[i]
            c2 = text[i+1]
            if c1 not in self.alphabet or c2 not in self.alphabet:
                raise ValueError("text contains chars not from alphabet")
            bigram_count[c1+c2] += 1
        return bigram_count

    def monogram_frequencies(self, text: str) -> dict[str, float]:
        monograms_count = {c: 0 for c in self.alphabet}
        total = len(text)
        if total == 0:
            return monograms_count
        for ch in text:
            if ch not in self.alphabet:
                raise ValueError("text contains chars not from alphabet")
            monograms_count[ch] += 1
        return {c: monograms_count[c] / total for c in self.alphabet}
    
    @staticmethod
    def calc_entropy(frequencies:dict[str, float]) -> float:
        entropy = 0
        for ngram in frequencies:
            frequency = frequencies[ngram]
            if frequency > 0:
                entropy -= frequency * math.log2(frequency)
        return entropy / len(list(frequencies.keys())[0])