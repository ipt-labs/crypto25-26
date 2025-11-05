import collections
import numpy as np

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

charMap = {char: i for i, char in enumerate(alphabet)}
intToChar = {i: char for i, char in enumerate(alphabet)}
langFreqs = np.array([frequencyNoSpaces.get(char, 0) for char in alphabet])
icCache = {}

def CleanInputText(text, alphabet=alphabet):
    text = text.lower().replace('ё', 'е').replace('ъ', 'ь')  
    cleaned = ''.join(c for c in text if c in alphabet)
  
    return cleaned

def IndexOfCoincidence(text, useCache=True):
    text = CleanInputText(text)
  
    if useCache and text in icCache:
        return icCache[text]
      
    n = len(text)
    counts = collections.Counter(text)
    coincidenceSum = sum(count * (count - 1) for count in counts.values())
    ic = coincidenceSum / (n * (n - 1))
  
    if useCache:
        icCache[text] = ic
      
    return ic

def TheoreticalIC(frequencies):
    return sum(p ** 2 for p in frequencies.values())

def findKeyLength(cipherText, min_block_length=50):
    icValues = {}
    text_length = len(cipherText)
  
    for r in range(2, 31):
        if text_length // r < min_block_length:  
            break
          
        blocks = [''] * r
        for i, char in enumerate(cipherText):
            blocks[i % r] += char
        avgIc = sum(IndexOfCoincidence(block) for block in blocks) / r if blocks else 0
        icValues[r] = avgIc
    bestR = max(icValues, key=icValues.get) if icValues else 2
  
    return bestR, icValues

def findKey(cipherText, r):
    blocks = [''] * r
    for i, char in enumerate(cipherText):
        blocks[i % r] += char
      
    key = ''
    details = []  
  
    for idx, block in enumerate(blocks):
        nBlock = len(block)
        if nBlock == 0:
            key += 'а'
            details.append({'block_index': idx, 'top_shifts': [('а', 0.0)]})
            continue
          
        blockIndex = np.array([charMap[c] for c in block])
        correlations = []
        for k in range(len(alphabet)):
            shifted_indices = (blockIndex - k) % len(alphabet)
            shifted_counts = np.bincount(shifted_indices, minlength=len(alphabet))
            blockFreqs = shifted_counts / nBlock
            currCorr = np.sum(langFreqs * blockFreqs)
            correlations.append((k, currCorr))
          
        correlations.sort(key=lambda x: x[1], reverse=True)
        top3 = [(intToChar[k], corr) for k, corr in correlations[:3]]
        bestK = correlations[0][0]
        key += intToChar[bestK]
        details.append({'block_index': idx, 'top_shifts': top3})
      
    return key, details

def VigenereDecode(cipherText, key, alphabet=alphabet):
    alphaSize = len(alphabet)
    decodedText = ''
    keyOffsets = [charMap[c] for c in key]
    pos = 0
  
    for char in cipherText:
        cipherIdx = charMap[char]
        keyIdx = keyOffsets[pos % len(key)]
        decodeIdx = (cipherIdx - keyIdx + alphaSize) % alphaSize
        decodedText += alphabet[decodeIdx]
        pos += 1
      
    return decodedText

if __name__ == "__main__":
    inputFile = 'VAR8.txt'
    with open(inputFile, 'r', encoding='utf-8') as file:
        cipherText = CleanInputText(file.read())

    print(f"Довжина шифртексту: {len(cipherText)} символів")
    print(f"Перші 50 символів шифртексту: {cipherText[:50]}...")
    icTheoretical = TheoreticalIC(frequencyNoSpaces)
    print(f"IC теоретичне для російської мови: {icTheoretical:.6f}")

    bestR, icValues = findKeyLength(cipherText)
    print("Таблиця середніх IC для можливих r:")
    print("----------------------------------------")
    print("| Довжина ключа (r) |Середній IC блоків|")
    print("|-------------------|------------------|")
    for r in sorted(icValues):
        print(f"| {r:<17} | {icValues[r]:.6f}         |")
    print("----------------------------------------")
    print(f"Найкраще r: {bestR} (максимальний середній IC: {icValues[bestR]:.6f}, близьке до теоретичного {icTheoretical:.6f})")

    _, keyDetails = findKey(cipherText, bestR)
    print("Деталі по блоках (зсуви з кореляціями для коригування):")
    for detail in keyDetails:
        print(f"Блок {detail['block_index']}:")
        for char, corr in detail['top_shifts']:
            print(f"  - Зсув '{char}' (k={charMap[char]}): кореляція {corr:.6f}")

    top_letters = []
    for i, detail in enumerate(keyDetails):
        top_char = detail['top_shifts'][0][0]
        top_letters.append(top_char)
        print(f"Позиція {i}: '{top_char}' (кореляція {detail['top_shifts'][0][1]:.6f})")

    key = ''.join(top_letters)
    print(f"Фінальний ключ: {key}")

    print("\nРозшифрування тексту")
    plainText = VigenereDecode(cipherText, key)
    print(f"IC розшифрованого тексту: {IndexOfCoincidence(plainText):.6f}")
    print("Перші 200 літер розшифрованого тексту:")
    print(plainText[:200] + "...")

    outputFile = 'DecryptedPlaintext_IC.txt'
    with open(outputFile, 'w', encoding='utf-8') as file:
        file.write(plainText)
    print(f"\nПовний розшифрований текст збережено у '{outputFile}'")
