import collections

alphabet = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'

frequencyNoSpaces = {
    'о': 0.11544, 'а': 0.082178, 'е': 0.082092, 'и': 0.067775, 'н': 0.065001,
    'т': 0.058421, 'с': 0.053992, 'л': 0.049969, 'в': 0.046128, 'р': 0.044141,
    'к': 0.034013, 'д': 0.030558, 'м': 0.029546, 'у': 0.027114, 'п': 0.02624,
    'я': 0.021932, 'ь': 0.019846, 'г': 0.019622, 'ы': 0.01931, 'б': 0.017327,
    'з': 0.017108, 'ч': 0.014416, 'й': 0.011617, 'ж': 0.010619, 'ш': 0.009239,
    'х': 0.008579, 'ю': 0.006116, 'ц': 0.003598, 'э': 0.003057, 'щ': 0.002954,
    'ф': 0.002054
}

def CleanInputText(text, alphabet=alphabet):
    text = text.lower().replace('ё', 'е').replace('ъ', 'ь')
    cleaned = ''.join(c for c in text if c in alphabet)
    return cleaned

def IndexOfCoincidence(text):
    text = CleanInputText(text) 
    n = len(text)
  
    counts = collections.Counter(text)
    coincidenceSum = sum(count * (count - 1) for count in counts.values())
    ic = coincidenceSum / (n * (n - 1))
  
    return ic

def TheoreticalIC(frequencies):
    return sum(p ** 2 for p in frequencies.values())

def ComputeICs(plaintextFile, cipherFiles):
    with open(plaintextFile, 'r', encoding='utf-8') as f:
        plainText = f.read()
      
    icPlain = IndexOfCoincidence(plainText)
    
    icTheoretical = TheoreticalIC(frequencyNoSpaces)
    
    icCiphers = {}
    for r, file in cipherFiles.items():
        with open(file, 'r', encoding='utf-8') as f:
            cipherText = f.read()
          
        icCiphers[r] = IndexOfCoincidence(cipherText)
    
    return icPlain, icTheoretical, icCiphers

if __name__ == "__main__":
    plaintextFile = 'PLAINTEXT.txt'
    cipherFiles = {r: f'cipher_r{r}.txt' for r in range(2, 31)}
    
    icPlain, icTheoretical, icCiphers = ComputeICs(plaintextFile, cipherFiles)
    
    print(f"IC теоретичне: {icTheoretical:.6f}")
    print(f"IC відкритого тексту: {icPlain:.6f}")
    print("----------------------------------------")
    print("| Довжина ключа (r) | IC для шифртексту|")
    print("|-------------------|------------------|")
  
    for r in sorted(icCiphers):
        print(f"| {r:<17} | {icCiphers[r]:.6f}         |")
    print("----------------------------------------")
