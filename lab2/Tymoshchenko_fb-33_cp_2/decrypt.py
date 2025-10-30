from collections import Counter

ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
M = len(ALPHABET)
INDEX = {ch: i for i, ch in enumerate(ALPHABET)}

FREQ = {
    'о':0.1097,'е':0.0845,'а':0.0801,'и':0.0735,'н':0.0670,'т':0.0626,'с':0.0547,
    'р':0.0473,'в':0.0454,'л':0.0434,'к':0.0349,'м':0.0321,'д':0.0281,'п':0.0281,
    'у':0.0262,'я':0.0201,'ы':0.0190,'ь':0.0174,'г':0.0169,'з':0.0165,'б':0.0159,
    'ч':0.0144,'й':0.0121,'х':0.0097,'ж':0.0094,'ш':0.0073,'ю':0.0064,'ц':0.0048,
    'щ':0.0036,'э':0.0032,'ъ':0.0004
}

def clean(t):
    t = t.lower().replace("ё","е")
    r = ""
    for c in t:
        if c in INDEX:
            r += c
    return r

def ioc(s):
    n = len(s)
    if n < 2:
        return 0
    f = Counter(s)
    top = 0
    for x in f.values():
        top += x*(x-1)
    return top/(n*(n-1))

def avg_ioc(text, L):
    parts = []
    for i in range(L):
        col = text[i::L]
        parts.append(ioc(col))
    return sum(parts)/len(parts)

def period(col):
    bestperiod = 0
    bestp = 1e9
    n = len(col)
    for s in range(M):
        period = 0
        f = Counter(col)
        for ch in ALPHABET:
            obs = f[ch]
            plain = ALPHABET[(INDEX[ch]-s)%M]
            exp = FREQ.get(plain,0)*n
            if exp>0:
                period += (obs-exp)**2/exp
        if period<bestp:
            bestp = period
            bestperiod = s
    return bestperiod

def decrypt(text, L):
    shifts = []
    cols = []
    for i in range(L):
        col = text[i::L]
        s = period(col)
        shifts.append(s)
        d = ""
        for ch in col:
            d += ALPHABET[(INDEX[ch]-s)%M]
        cols.append(d)
    plain = ""
    for i in range(len(text)):
        plain += cols[i%L][i//L]
    key = "".join(ALPHABET[s] for s in shifts)
    return key, plain

filename = "шт.txt"

with open(filename,"r",encoding="utf-8") as f:
    text = f.read()

text = clean(text)

ioc_scores = []
for L in range(2,33):
    score = avg_ioc(text, L)
    ioc_scores.append((L, score))

ioc_scores.sort(key=lambda x: x[1], reverse=True)

top_L = [x[0] for x in ioc_scores[:1]]

for L in top_L:
    key, decoded = decrypt(text, L)
    print("="*50)
    print(f"Довжина ключа: {L} | Ключ: {key}")
    print("Початок тексту:")
    print(decoded[:1000])
