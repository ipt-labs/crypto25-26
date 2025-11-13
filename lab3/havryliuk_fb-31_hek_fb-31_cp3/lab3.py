import os
import sys
import time
from collections import defaultdict
from modular_math import vyrishyty_liniyне_porivnyannya, znayty_obernenyy_element
from text_analyzer import (
    ROZMIR_ALFAVITU, bihrama_do_chysla, chyslo_do_bihramy, 
    ochystyty_shyfrotekst, otrymaty_top_bihramy, otsinyty_yakist_tekstu,
    pidrahuvaty_chastoty_bihram, obchyslyty_entropiyu, pidrahuvaty_chastoty_symvoliv
)

KATALOH_SKRYPTU = os.path.dirname(os.path.abspath(__file__))
MODUL_V_KVADRATI = ROZMIR_ALFAVITU * ROZMIR_ALFAVITU

NAYCHASTISHI_ROSIYSIKI_BIHRAMY = ["ст", "но", "то", "на", "ен"]


def deshyfruvaty_tekst(shyfrotekst, kluch_a, kluch_b):
    obernenyy_a = znayty_obernenyy_element(kluch_a, MODUL_V_KVADRATI)
    if obernenyy_a is None:
        return None
    
    symvoly_vidkrytoho = []
    
    for pozyciya in range(0, len(shyfrotekst) - 1, 2):
        bihrama_shyfru = shyfrotekst[pozyciya:pozyciya + 2]
        if len(bihrama_shyfru) != 2:
            break
        
        znachennya_Y = bihrama_do_chysla(bihrama_shyfru[0], bihrama_shyfru[1])
        if znachennya_Y is None:
            return None
        
        znachennya_X = (obernenyy_a * (znachennya_Y - kluch_b)) % MODUL_V_KVADRATI
        bihrama_vidkryta = chyslo_do_bihramy(znachennya_X)
        
        if bihrama_vidkryta is None:
            return None
        
        symvoly_vidkrytoho.append(bihrama_vidkryta)
    
    return ''.join(symvoly_vidkrytoho)


def znayty_kandydaty_klyucha(bihrama_vid1, bihrama_vid2, bihrama_shyf1, bihrama_shyf2):
    X1 = bihrama_do_chysla(bihrama_vid1[0], bihrama_vid1[1])
    X2 = bihrama_do_chysla(bihrama_vid2[0], bihrama_vid2[1])
    Y1 = bihrama_do_chysla(bihrama_shyf1[0], bihrama_shyf1[1])
    Y2 = bihrama_do_chysla(bihrama_shyf2[0], bihrama_shyf2[1])
    
    if None in [X1, X2, Y1, Y2]:
        return []
    
    riznytsya_Y = (Y1 - Y2) % MODUL_V_KVADRATI
    riznytsya_X = (X1 - X2) % MODUL_V_KVADRATI
    
    if riznytsya_X == 0:
        return []
    
    mozhlyvi_znachennya_a = vyrishyty_liniyне_porivnyannya(riznytsya_X, riznytsya_Y, MODUL_V_KVADRATI)
    
    kandydaty_klyuchiv = []
    
    for znachennya_a in mozhlyvi_znachennya_a:
        if znayty_obernenyy_element(znachennya_a, MODUL_V_KVADRATI) is None:
            continue
        
        znachennya_b = (Y1 - znachennya_a * X1) % MODUL_V_KVADRATI
        
        perevirka_Y2 = (znachennya_a * X2 + znachennya_b) % MODUL_V_KVADRATI
        if perevirka_Y2 == Y2:
            kandydaty_klyuchiv.append((znachennya_a, znachennya_b))
    
    return kandydaty_klyuchiv


def kryptoanaliz_sfokusovanyy(fayl_shyfrotekstu):
    print("\n" + "="*70)
    print("КРИПТОАНАЛІЗ АФІННОГО БІГРАМНОГО ШИФРУ")
    print("="*70 + "\n")
    
    shlyakh_faylu = os.path.join(KATALOH_SKRYPTU, fayl_shyfrotekstu)
    print(f"Читання: {fayl_shyfrotekstu}")
    
    with open(shlyakh_faylu, 'r', encoding='utf-8') as f:
        neprybranyy_tekst = f.read()
    
    ochyschennyy = ochystyty_shyfrotekst(neprybranyy_tekst)
    print(f" Очищено: {len(ochyschennyy)} символів")
    print(f" Біграм: {len(ochyschennyy)//2}\n")
    
    print("="*70)
    print("ЧАСТОТНИЙ АНАЛІЗ ШИФРТЕКСТУ")
    print("="*70 + "\n")
    
    top5_shyfru = otrymaty_top_bihramy(ochyschennyy, kilkist_top=5, z_peretynom=False)
    chastoty_shyfru = pidrahuvaty_chastoty_bihram(ochyschennyy, z_peretynom=False)
    
    print("Топ-5 найчастіших біграм у шифртексті:")
    for i, bh in enumerate(top5_shyfru, 1):
        chastota = chastoty_shyfru.get(bh, 0)
        print(f"  {i}. '{bh}' - {chastota:.4f} ({int(chastota * len(ochyschennyy)//2)} разів)")
    
    print("\nТоп-5 біграм російської мови (еталон):")
    for i, bh in enumerate(NAYCHASTISHI_ROSIYSIKI_BIHRAMY, 1):
        print(f"  {i}. '{bh}'")
    
    print("\n" + "="*70)
    print("ПОШУК КЛЮЧІВ")
    print("="*70 + "\n")
    
    print("Перебираємо всі можливі співставлення топ-5 біграм...")
    print("(Всього комбінацій пар: 5×4 × 5×4 / 2 = 200)\n")
    
    usi_kandydaty_klyuchiv = set()
    perevireno_kombinatsiy = 0
    
    for i in range(5):
        for j in range(5):
            if i == j:
                continue
            
            bihrama_vid1 = NAYCHASTISHI_ROSIYSIKI_BIHRAMY[i]
            bihrama_vid2 = NAYCHASTISHI_ROSIYSIKI_BIHRAMY[j]
            
            for k in range(5):
                for l in range(5):
                    if k == l:
                        continue
                    
                    bihrama_shyf1 = top5_shyfru[k]
                    bihrama_shyf2 = top5_shyfru[l]
                    
                    perevireno_kombinatsiy += 1
                    
                    klyuchi = znayty_kandydaty_klyucha(
                        bihrama_vid1, bihrama_vid2,
                        bihrama_shyf1, bihrama_shyf2
                    )
                    
                    for kluch in klyuchi:
                        usi_kandydaty_klyuchiv.add(kluch)
    
    print(f" Перевірено комбінацій: {perevireno_kombinatsiy}")
    print(f" Знайдено унікальних ключів: {len(usi_kandydaty_klyuchiv)}\n")
    
    if not usi_kandydaty_klyuchiv:
        print("✗ Не знайдено жодного ключа!")
        return []
    
    print("="*70)
    print("ДЕШИФРУВАННЯ ТА ОЦІНКА ЗМІСТОВНОСТІ")
    print("="*70 + "\n")
    
    rezultaty = []
    
    print(f"Дешифрую {len(usi_kandydaty_klyuchiv)} варіантів...")
    
    for indeks, (kluch_a, kluch_b) in enumerate(usi_kandydaty_klyuchiv, 1):
        if indeks % 50 == 0:
            print(f"  Оброблено: {indeks}/{len(usi_kandydaty_klyuchiv)}")
        
        vidkrytyy_tekst = deshyfruvaty_tekst(ochyschennyy, kluch_a, kluch_b)
        
        if vidkrytyy_tekst and '??' not in vidkrytyy_tekst:
            otsinka_yakosti = otsinyty_yakist_tekstu(vidkrytyy_tekst)
            
            chastoty_mono = pidrahuvaty_chastoty_symvoliv(vidkrytyy_tekst)
            h1 = obchyslyty_entropiyu(chastoty_mono)
            
            chastoty_bihram = pidrahuvaty_chastoty_bihram(vidkrytyy_tekst, z_peretynom=True)
            h2 = obchyslyty_entropiyu(chastoty_bihram)
            
            rezultaty.append({
                'kluch_a': kluch_a,
                'kluch_b': kluch_b,
                'tekst': vidkrytyy_tekst,
                'otsinka': otsinka_yakosti,
                'h1': h1,
                'h2': h2
            })
    
    print(f" Успішно дешифровано: {len(rezultaty)} варіантів\n")
    
    rezultaty.sort(key=lambda x: x['otsinka'], reverse=True)
    
    print("="*70)
    print("ТОП-10 РЕЗУЛЬТАТІВ")
    print("="*70 + "\n")
    
    for indeks, rez in enumerate(rezultaty[:10], 1):
        print(f"{'─'*70}")
        print(f"#{indeks}  Ключ: a={rez['kluch_a']}, b={rez['kluch_b']}")
        print(f"     Оцінка: {rez['otsinka']:.1f}/100")
        print(f"     H1: {rez['h1']:.4f}, H2: {rez['h2']:.4f}")
        print(f"{'─'*70}")
        print(rez['tekst'][:200])
        print()
    
    vyhidnyy_fayl = 'rezultaty.txt'
    shlyakh_vyhodu = os.path.join(KATALOH_SKRYPTU, vyhidnyy_fayl)
    
    with open(shlyakh_vyhodu, 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write("РЕЗУЛЬТАТИ КРИПТОАНАЛІЗУ АФІННОГО БІГРАМНОГО ШИФРУ\n")
        f.write("="*70 + "\n\n")
        
        f.write(f"Файл: {fayl_shyfrotekstu}\n")
        f.write(f"Довжина шифртексту: {len(ochyschennyy)} символів\n")
        f.write(f"Знайдено варіантів: {len(rezultaty)}\n\n")
        
        f.write("Топ-5 біграм шифртексту:\n")
        for i, bh in enumerate(top5_shyfru, 1):
            chastota = chastoty_shyfru.get(bh, 0)
            f.write(f"  {i}. '{bh}' - {chastota:.4f}\n")
        f.write("\n")
        
        for indeks, rez in enumerate(rezultaty[:30], 1):
            f.write(f"\n{'='*70}\n")
            f.write(f"ВАРІАНТ #{indeks}\n")
            f.write(f"{'='*70}\n")
            f.write(f"Ключ: a = {rez['kluch_a']}, b = {rez['kluch_b']}\n")
            f.write(f"Оцінка змістовності: {rez['otsinka']:.2f}/100\n")
            f.write(f"Ентропія монограм (H1): {rez['h1']:.4f}\n")
            f.write(f"Ентропія біграм (H2): {rez['h2']:.4f}\n\n")
            f.write("РОЗШИФРОВАНИЙ ТЕКСТ:\n")
            f.write("-"*70 + "\n")
            f.write(rez['tekst'])
            f.write("\n\n")
    
    print(f" Результати збережено: {vyhidnyy_fayl}\n")
    
    return rezultaty


if __name__ == "__main__":
    pochatok_chasu = time.time()
    
    fayl_shyfrotekstu = '06_from_folder_variants_utf8.txt'
    if len(sys.argv) > 1:
        fayl_shyfrotekstu = sys.argv[1]
    
    rezultaty = kryptoanaliz_sfokusovanyy(fayl_shyfrotekstu)
    
    vitrachenyy_chas = time.time() - pochatok_chasu
    
    print("="*70)
    print(f"ЧАС ВИКОНАННЯ: {vitrachenyy_chas:.1f} секунд ({vitrachenyy_chas/60:.1f} хвилин)")
    print("="*70 + "\n")
    
    if rezultaty:
        naykrashchyy = rezultaty[0]
        print(" НАЙКРАЩИЙ РЕЗУЛЬТАТ:")
        print(f"Ключ: a = {naykrashchyy['kluch_a']}, b = {naykrashchyy['kluch_b']}")
        print(f"Оцінка: {naykrashchyy['otsinka']:.1f}/100")
        print(f"H1 = {naykrashchyy['h1']:.4f}, H2 = {naykrashchyy['h2']:.4f}")
        print(f"\nПочаток тексту:")
        print(naykrashchyy['tekst'][:300])
        
        if naykrashchyy['otsinka'] > 60:
            print("\n ТЕКСТ ВИГЛЯДАЄ ЗМІСТОВНИМ!")
        elif naykrashchyy['otsinka'] > 40:
            print("\n⚠ Текст може бути правильним, але потребує перевірки")
        else:
            print("\n⚠ Можливо потрібно розширити пошук або перевірити алфавіт")
    else:
        print("✗ Не знайдено жодного варіанту")
        print("\n<ПРОПОЗИЦІЇ ДЛЯ НАЛАГОДЖЕННЯ>:")
        print("1. Перевірте що файл має правильне кодування (UTF-8)")
        print("2. Перевірте що алфавіт співпадає з тим, який використовувався при шифруванні")
        print("3. Спробуйте файл 'for_test' для тестування")
