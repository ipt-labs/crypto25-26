from collections import Counter

alphabet = 'абвгдежзийклмнопрстуфхцчшщьыэюя'

alphabet_size = len(alphabet)
modulus = alphabet_size ** 2

letter_to_number = {letter: idx for idx, letter in enumerate(alphabet)}
number_to_letter = {idx: letter for idx, letter in enumerate(alphabet)}

def bigram_to_num(bigram):
    if len(bigram) != 2:
        return None
      
    return letter_to_number.get(bigram[0]) * alphabet_size + letter_to_number.get(bigram[1])

def num_to_bigram(number):
    return number_to_letter.get(number // alphabet_size) + number_to_letter.get(number % alphabet_size)

def get_top_bigrams(text, count=5):
    even_length_text = text[:len(text) // 2 * 2]
    bigrams = [even_length_text[i:i+2] for i in range(0, len(even_length_text), 2)]
  
    return Counter(bigrams).most_common(count)

def extended_euclid(a, b):
    x0, x1 = 1, 0
    y0, y1 = 0, 1
  
    while b != 0:
        q = a // b
        a, b = b, a % b
        x0, x1 = x1, x0 - q * x1
        y0, y1 = y1, y0 - q * y1
      
    return a, x0, y0

def modular_inverse(a, mod):
    gcd, x, _ = extended_euclid(a, mod)
    if gcd != 1:
        return None
      
    return x % mod

def solve_linear_congruence(coeff, target, mod):
    gcd, _, _ = extended_euclid(coeff, mod)
    if target % gcd != 0:
        return []
      
    reduced_coeff = coeff // gcd
    reduced_target = target // gcd
    reduced_mod = mod // gcd
  
    inv = modular_inverse(reduced_coeff, reduced_mod)
  
    if inv is None:
        return []
      
    base = (inv * reduced_target) % reduced_mod
    solutions = [(base + i * reduced_mod) % mod for i in range(gcd)]
  
    return [sol for sol in solutions if extended_euclid(sol, mod)[0] == 1]
