# scoring.py
from utils import alphabet, bigram_to_num, num_to_bigram, modular_inverse, modulus

common_letters = ['о', 'а', 'е', 'и', 'н', 'т']
rare_letters = ['ф', 'щ', 'ц', 'э', 'ж', 'ш', 'х', 'ю']
common_overlapping_bigrams = ['то', 'ор', 'ро', 'ов', 'во', 'ос', 'ст', 'та', 'ан', 'на', 'ра', 'ал', 'ли', 'ин', 'ни', 'ис', 'ск', 'ко', 'от', 'те']

def score_as_russian(text, min_length=100):
    if len(text) < min_length:
        return -float('inf'), {}
      
    cleaned_text = ''.join(c for c in text if c in alphabet)
    text_length = len(cleaned_text)
  
    if text_length == 0:
        return -float('inf'), {}
      
    letter_frequencies = {letter: cleaned_text.count(letter) / text_length for letter in alphabet}
  
    common_freq_sum = sum(letter_frequencies.get(letter, 0) for letter in common_letters)
    rare_freq_sum = sum(letter_frequencies.get(letter, 0) for letter in rare_letters)
  
    overlapping_bigrams = [cleaned_text[i:i+2] for i in range(1, text_length - 1, 2)]
    overlap_ratio = sum(1 for bigram in overlapping_bigrams if bigram in common_overlapping_bigrams) / (len(overlapping_bigrams) or 1)
    score = 200 * common_freq_sum - 100 * max(0, rare_freq_sum - 0.02) + 300 * overlap_ratio
  
    return score, {'common_freq_sum': common_freq_sum, 'rare_freq_sum': rare_freq_sum, 'overlap_ratio': overlap_ratio}

def decrypt_ciphertext(ciphertext, a, b):
    inv_a = modular_inverse(a, modulus)
  
    if inv_a is None:
        return None
      
    cleaned_ciphertext = ''.join(c for c in ciphertext if c in alphabet)
    cleaned_ciphertext = cleaned_ciphertext[:len(cleaned_ciphertext) // 2 * 2]
  
    plaintext = ''
    for i in range(0, len(cleaned_ciphertext), 2):
        cipher_bigram_num = bigram_to_num(cleaned_ciphertext[i:i+2])
        plain_bigram_num = (inv_a * (cipher_bigram_num - b)) % modulus
        plaintext += num_to_bigram(plain_bigram_num)
      
    return plaintext
