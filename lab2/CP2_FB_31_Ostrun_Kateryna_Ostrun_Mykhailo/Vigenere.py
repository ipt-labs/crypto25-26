ALPHABET = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'

def CleanInputText(text, alphabet=ALPHABET):
    text = text.lower().replace('ё', 'е').replace('ъ', 'ь')  
    cleaned = ''.join(c for c in text if c in alphabet)
    return cleaned

def VigenereEncode(plainText, key, alphabet=ALPHABET):
    alphaSize = len(alphabet)
    charMap = {char: index for index, char in enumerate(alphabet)}
    encodedText = ''
  
    keySize = len(key)
    keyOffsets = [charMap[c] for c in key]
    pos = 0
  
    for char in plainText:
        plainIdx = charMap[char]
        keyIdx = keyOffsets[pos % keySize]
        encodeIdx = (plainIdx + keyIdx) % alphaSize
        encodedText += alphabet[encodeIdx]
        pos += 1
      
    return encodedText

def CreateCipherFiles(inputFile):
    with open(inputFile, 'r', encoding='utf-8') as file:
        sourceText = file.read()
    plainText = CleanInputText(sourceText)
  
    keys = {
        2: 'ео', 3: 'яйа', 4: 'ьндш', 5: 'аыщць', 
        6: 'пийсыд', 7: 'ынщсуэд', 8: 'ьефчяяот', 9: 'зззюухнмг', 
        10: 'уняфбйбгиф', 11: 'щнкбпссюзпщ', 12: 'цькюэуыяцйлэ', 
        13: 'ртйыйвюлвжщчэ', 14: 'юисзшсюкзцувжо', 15: 'чэозюсшещыблждй', 
        16: 'эрлээыцюгщдяцаяа', 17: 'бщецезлсочэлызузн',18: 'чухяджофрхпбгшмыхц', 
        19: 'пюасяхтэнюбьоймччов', 20: 'гхщтьацнсгахмоорнеба', 
        21: 'збспоижеывбенобмъоьса', 22: 'кыхсйнхжешжццрвэзшетчм', 23: 'двотеожшсэчкчцнсдкпкэшс', 
        24: 'офговфщсднфнящэйрипрыщчо', 25: 'ияегзйкыдшшэразсхзтыкэарл', 
        26: 'жумйчкафябзчупгпееядииюкры', 27: 'нмущчььзподхбооадгодвхдпсян', 
        28: 'июпюъмжжыцыъэгжгщхжпммьиылсэ', 29: 'пдьжгаепкъяюнщгкшашрэтыяймтнг', 
        30: 'гфггюкгелддпщзпвеъфрнфпрщиуэфд'
    }
  
    for length, key in keys.items():
        print(f"Ключ довжини {length}: {key}")
        cipherText = VigenereEncode(plainText, key)
      
        with open(f'cipher_r{length}.txt', 'w', encoding='utf-8') as file:
            file.write(cipherText)

if __name__ == "__main__":
    inputFile = 'PLAINTEXT.txt'  
    CreateCipherFiles(inputFile)
