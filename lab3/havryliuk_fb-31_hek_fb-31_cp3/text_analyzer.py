from collections import defaultdict
import math


ROSIYSKYY_ALFAVIT = 'абвгдежзийклмнопрстуфхцчшщьыэюя'
ROZMIR_ALFAVITU = 31


def symvol_do_chysla(symvol):
    if symvol in ROSIYSKYY_ALFAVIT:
        return ROSIYSKYY_ALFAVIT.index(symvol)
    return None


def chyslo_do_symvolu(chyslo):
    if 0 <= chyslo < ROZMIR_ALFAVITU:
        return ROSIYSKYY_ALFAVIT[chyslo]
    return None


def bihrama_do_chysla(symvol1, symvol2):
    chyslo1 = symvol_do_chysla(symvol1)
    chyslo2 = symvol_do_chysla(symvol2)
    
    if chyslo1 is None or chyslo2 is None:
        return None
    
    return chyslo1 * ROZMIR_ALFAVITU + chyslo2


def chyslo_do_bihramy(chyslo):
    if chyslo < 0 or chyslo >= ROZMIR_ALFAVITU * ROZMIR_ALFAVITU:
        return None
    
    chyslo_symvolu1 = chyslo // ROZMIR_ALFAVITU
    chyslo_symvolu2 = chyslo % ROZMIR_ALFAVITU
    
    return chyslo_do_symvolu(chyslo_symvolu1) + chyslo_do_symvolu(chyslo_symvolu2)


def pidrahuvaty_chastoty_bihram(tekst, z_peretynom=False):
    pidrahunok_bihram = defaultdict(int)
    zahalna_kilkist = 0
    
    if z_peretynom:
        for pozyciya in range(len(tekst) - 1):
            bihrama = tekst[pozyciya:pozyciya + 2]
            if len(bihrama) == 2:
                pidrahunok_bihram[bihrama] += 1
                zahalna_kilkist += 1
    else:
        for pozyciya in range(0, len(tekst) - 1, 2):
            if pozyciya + 1 < len(tekst):
                bihrama = tekst[pozyciya:pozyciya + 2]
                if len(bihrama) == 2:
                    pidrahunok_bihram[bihrama] += 1
                    zahalna_kilkist += 1
    
    if zahalna_kilkist == 0:
        return {}
    
    return {bh: kilkist / zahalna_kilkist for bh, kilkist in pidrahunok_bihram.items()}


def pidrahuvaty_chastoty_symvoliv(tekst):
    pidrahunok_symvoliv = defaultdict(int)
    zahalna_kilkist = len(tekst)
    
    if zahalna_kilkist == 0:
        return {}
    
    for symvol in tekst:
        if symvol in ROSIYSKYY_ALFAVIT:
            pidrahunok_symvoliv[symvol] += 1
    
    return {sym: kilkist / zahalna_kilkist for sym, kilkist in pidrahunok_symvoliv.items()}


def obchyslyty_entropiyu(chastoty):
    if not chastoty:
        return 0.0
    
    suma_entropiyi = 0.0
    dovzhyna_nhramy = len(list(chastoty.keys())[0]) if chastoty else 1
    
    for nhrama, chastota in chastoty.items():
        if chastota > 0:
            suma_entropiyi -= chastota * math.log2(chastota)
    
    return suma_entropiyi / dovzhyna_nhramy


def otsinyty_yakist_tekstu(tekst):
    if len(tekst) < 20:
        return 0.0
    
    otsinka = 0.0
    
    chastoty_mono = pidrahuvaty_chastoty_symvoliv(tekst)
    h1 = obchyslyty_entropiyu(chastoty_mono)
    
    if 4.2 <= h1 <= 4.6:
        otsinka += 25.0
    elif 4.0 <= h1 <= 4.8:
        otsinka += 15.0
    elif h1 > 5.0:
        otsinka -= 20.0
    
    chastoty_bihram_peretyn = pidrahuvaty_chastoty_bihram(tekst, z_peretynom=True)
    h2 = obchyslyty_entropiyu(chastoty_bihram_peretyn)
    
    if 3.9 <= h2 <= 4.3:
        otsinka += 25.0
    elif 3.7 <= h2 <= 4.5:
        otsinka += 15.0
    elif h2 > 4.8:
        otsinka -= 20.0
    
    chasti_litery = 'оаеит'
    suma_chastykh = sum(chastoty_mono.get(l, 0) for l in chasti_litery)
    
    if 0.35 <= suma_chastykh <= 0.50:
        otsinka += 20.0
    elif 0.30 <= suma_chastykh <= 0.55:
        otsinka += 10.0
    
    ridkisni_litery = 'фщьыэюя'
    suma_ridkisnykh = sum(chastoty_mono.get(l, 0) for l in ridkisni_litery)
    
    if 0.05 <= suma_ridkisnykh <= 0.15:
        otsinka += 15.0
    elif 0.03 <= suma_ridkisnykh <= 0.18:
        otsinka += 7.0
    
    podviyni_litery = sum(1 for i in range(len(tekst)-1) if tekst[i] == tekst[i+1])
    vidnoshennya_podviynykh = podviyni_litery / (len(tekst) - 1)
    
    if 0.005 <= vidnoshennya_podviynykh <= 0.06:
        otsinka += 15.0
    elif vidnoshennya_podviynykh > 0.15:
        otsinka -= 15.0
    
    return max(0.0, min(100.0, otsinka))


def ochystyty_shyfrotekst(neprybranyy_tekst):
    ochyschennyy = neprybranyy_tekst.lower()
    ochyschennyy = ochyschennyy.replace('ё', 'е')
    ochyschennyy = ochyschennyy.replace('ъ', 'ь')
    
    rezultat = ''
    for symvol in ochyschennyy:
        if symvol in ROSIYSKYY_ALFAVIT:
            rezultat += symvol
    
    return rezultat


def otrymaty_top_bihramy(tekst, kilkist_top=5, z_peretynom=False):
    chastoty = pidrahuvaty_chastoty_bihram(tekst, z_peretynom=z_peretynom)
    sortovani_bihramy = sorted(chastoty.items(), key=lambda x: x[1], reverse=True)
    return [bh for bh, _ in sortovani_bihramy[:kilkist_top]]
