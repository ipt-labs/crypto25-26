import math
from collections import defaultdict
import sys

class DualOutput:
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, 'w', encoding='utf-8')
    
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
    
    def flush(self):
        self.terminal.flush()
        self.log.flush()
    
    def close(self):
        self.log.close()
























def ochystyty_tekst(raw_text):
    cleaned = raw_text.lower()
    cleaned = cleaned.replace('ё', 'е')
    cleaned = cleaned.replace('ъ', 'ь')
    
    dozvol_symvoly = 'абвгдежзийклмнопрстуфхцчшщьыэюя '
    rezultat = ''
    for symvol in cleaned:
        if symvol in dozvol_symvoly:
            rezultat += symvol
    
    while '  ' in rezultat:
        rezultat = rezultat.replace('  ', ' ')
    
    return rezultat.strip()


def pidrahuvaty_chastoty_symvoliv(tekst):
    kilkist_symvoliv = defaultdict(int)
    
    for litera in tekst:
        kilkist_symvoliv[litera] += 1
    
    zahalna_kilkist = len(tekst)
    ymovirnist_map = {}
    
    for symvol, kilkist in kilkist_symvoliv.items():
        ymovirnist_map[symvol] = kilkist / zahalna_kilkist
    
    return ymovirnist_map, kilkist_symvoliv


def pidrahuvaty_bihramy_peretyn(tekst):
    bihramy_counter = defaultdict(int)
    
    for pozyciya in range(len(tekst) - 1):
        bihrama = tekst[pozyciya:pozyciya + 2]
        bihramy_counter[bihrama] += 1
    
    zahalna_kilkist_bihram = len(tekst) - 1
    ymovirnist_bihram = {}
    
    for bihrama, kilkist in bihramy_counter.items():
        ymovirnist_bihram[bihrama] = kilkist / zahalna_kilkist_bihram
    
    return ymovirnist_bihram, bihramy_counter


def pidrahuvaty_bihramy_bez_peretynu(tekst):
    bihramy_counter = defaultdict(int)
    
    for pozyciya in range(0, len(tekst) - 1, 2):
        bihrama = tekst[pozyciya:pozyciya + 2]
        if len(bihrama) == 2:
            bihramy_counter[bihrama] += 1
    
    zahalna_kilkist = sum(bihramy_counter.values())
    ymovirnist_bihram = {}
    
    for bihrama, kilkist in bihramy_counter.items():
        ymovirnist_bihram[bihrama] = kilkist / zahalna_kilkist
    
    return ymovirnist_bihram, bihramy_counter


def obchyslyty_entropiyu(ymovirnist_slovnyk):
    entropia_suma = 0.0
    
    for symvol, ymovirnist in ymovirnist_slovnyk.items():
        if ymovirnist > 0:
            entropia_suma -= ymovirnist * math.log2(ymovirnist)
    
    return entropia_suma


def vykorystaty_tablycyu_chastot(kilkist_dict, zagalna_kst):
    sorted_items = sorted(kilkist_dict.items(), key=lambda x: x[1], reverse=True)
    
    print(f"{'Символ':<10} {'Кількість':<12} {'Ймовірність':<15}")
    print("-" * 40)
    
    for symvol, kilkist in sorted_items:
        ymovirnist = kilkist / zagalna_kst
        display_sym = '_' if symvol == ' ' else symvol
        print(f"{display_sym:<10} {kilkist:<12} {ymovirnist:<15.6f}")


def vykorystaty_matrycyu_bihram(bihramy_dict):
    sorted_bihrams = sorted(bihramy_dict.items(), key=lambda x: x[1], reverse=True)
    
    print(f"\n{'Біграма':<10} {'Кількість':<12}")
    print("-" * 25)
    
    for bihrama, kilkist in sorted_bihrams[:20]:
        display_bg = bihrama.replace(' ', '_')
        print(f"{display_bg:<10} {kilkist:<12}")


















def main():
    output_handler = DualOutput('results.txt')
    sys.stdout = output_handler
    
    try:
        print("Читаю файл test.txt...")
        with open('test.txt', 'r', encoding='utf-8') as file:
            original_tekst = file.read()
        
        print(f"Розмір оригінального тексту: {len(original_tekst)} символів\n")
        
        ochyschenyy_tekst = ochystyty_tekst(original_tekst)
        print(f"Розмір після фільтрації: {len(ochyschenyy_tekst)} символів\n")
        
        print("=" * 50)
        print("АНАЛІЗ ТЕКСТУ З ПРОБІЛАМИ")
        print("=" * 50)
        
        prob_symvoliv, kilkist_symvoliv = pidrahuvaty_chastoty_symvoliv(ochyschenyy_tekst)
        
        print("\nТаблиця частот символів:")
        vykorystaty_tablycyu_chastot(kilkist_symvoliv, len(ochyschenyy_tekst))
        
        h1_z_probilamy = obchyslyty_entropiyu(prob_symvoliv)
        print(f"\n>>> H1 (з пробілами) = {h1_z_probilamy:.4f} біт\n")
        
        print("\nПідраховую біграми з перетином...")
        prob_bihram_peretyn, kilkist_bihram_peretyn = pidrahuvaty_bihramy_peretyn(ochyschenyy_tekst)
        
        print("Найчастіші біграми (з перетином):")
        vykorystaty_matrycyu_bihram(kilkist_bihram_peretyn)
        
        h_x1x2_peretyn = obchyslyty_entropiyu(prob_bihram_peretyn)
        h2_peretyn = h_x1x2_peretyn / 2
        print(f"\n>>> H2 (з пробілами, перетин) = {h2_peretyn:.4f} біт")
        print(f"    H(x1,x2) = {h_x1x2_peretyn:.4f} біт\n")
        
        print("Підраховую біграми без перетину...")
        prob_bihram_bez, kilkist_bihram_bez = pidrahuvaty_bihramy_bez_peretynu(ochyschenyy_tekst)
        
        print("Найчастіші біграми (без перетину):")
        vykorystaty_matrycyu_bihram(kilkist_bihram_bez)
        
        h_x1x2_bez = obchyslyty_entropiyu(prob_bihram_bez)
        h2_bez = h_x1x2_bez / 2
        print(f"\n>>> H2 (з пробілами, без перетину) = {h2_bez:.4f} біт")
        print(f"    H(x1,x2) = {h_x1x2_bez:.4f} біт\n")
        
        print("\n" + "=" * 50)
        print("АНАЛІЗ ТЕКСТУ БЕЗ ПРОБІЛІВ")
        print("=" * 50)
        
        tekst_bez_probiliv = ochyschenyy_tekst.replace(' ', '')
        print(f"\nРозмір тексту без пробілів: {len(tekst_bez_probiliv)} символів\n")
        
        prob_symv_bez, kilkist_symv_bez = pidrahuvaty_chastoty_symvoliv(tekst_bez_probiliv)
        
        print("Таблиця частот символів:")
        vykorystaty_tablycyu_chastot(kilkist_symv_bez, len(tekst_bez_probiliv))
        
        h1_bez_probiliv = obchyslyty_entropiyu(prob_symv_bez)
        print(f"\n>>> H1 (без пробілів) = {h1_bez_probiliv:.4f} біт\n")
        
        print("Підраховую біграми з перетином...")
        prob_bih_bez_peretyn, kilkist_bih_bez_peretyn = pidrahuvaty_bihramy_peretyn(tekst_bez_probiliv)
        
        print("Найчастіші біграми (з перетином):")
        vykorystaty_matrycyu_bihram(kilkist_bih_bez_peretyn)
        
        h_x1x2_bez_peretyn = obchyslyty_entropiyu(prob_bih_bez_peretyn)
        h2_bez_peretyn = h_x1x2_bez_peretyn / 2
        print(f"\n>>> H2 (без пробілів, перетин) = {h2_bez_peretyn:.4f} біт")
        print(f"    H(x1,x2) = {h_x1x2_bez_peretyn:.4f} біт\n")
        
        print("Підраховую біграми без перетину...")
        prob_bih_bez_bez, kilkist_bih_bez_bez = pidrahuvaty_bihramy_bez_peretynu(tekst_bez_probiliv)
        
        print("Найчастіші біграми (без перетину):")
        vykorystaty_matrycyu_bihram(kilkist_bih_bez_bez)
        
        h_x1x2_bez_bez = obchyslyty_entropiyu(prob_bih_bez_bez)
        h2_bez_bez = h_x1x2_bez_bez / 2
        print(f"\n>>> H2 (без пробілів, без перетину) = {h2_bez_bez:.4f} біт")
        print(f"    H(x1,x2) = {h_x1x2_bez_bez:.4f} біт\n")
        
        print("\n" + "=" * 50)
        print("ПІДСУМКОВІ РЕЗУЛЬТАТИ")
        print("=" * 50)
        print(f"\nЗ ПРОБІЛАМИ:")
        print(f"  H1 = {h1_z_probilamy:.4f} біт")
        print(f"  H2 (перетин) = {h2_peretyn:.4f} біт")
        print(f"  H2 (без перетину) = {h2_bez:.4f} біт")
        
        print(f"\nБЕЗ ПРОБІЛІВ:")
        print(f"  H1 = {h1_bez_probiliv:.4f} біт")
        print(f"  H2 (перетин) = {h2_bez_peretyn:.4f} біт")
        print(f"  H2 (без перетину) = {h2_bez_bez:.4f} біт")
        






        h0_z_probilamy = math.log2(33)
        h0_bez_probiliv = math.log2(32)
        
        r_h1_z = 1 - h1_z_probilamy / h0_z_probilamy
        r_h1_bez = 1 - h1_bez_probiliv / h0_bez_probiliv
        
        r_h2_peretyn_z = 1 - h2_peretyn / h0_z_probilamy
        r_h2_bez_peretyn_z = 1 - h2_bez / h0_z_probilamy
        
        r_h2_peretyn_bez = 1 - h2_bez_peretyn / h0_bez_probiliv
        r_h2_bez_peretyn_bez = 1 - h2_bez_bez / h0_bez_probiliv
        

















        print(f"\nНАДЛИШКОВІСТЬ:")
        print(f"\nМодель H1:")
        print(f"  R (з пробілами) = {r_h1_z:.4f} ({r_h1_z*100:.2f}%)")
        print(f"  R (без пробілів) = {r_h1_bez:.4f} ({r_h1_bez*100:.2f}%)")
        
        print(f"\nМодель H2 (з перетином):")
        print(f"  R (з пробілами) = {r_h2_peretyn_z:.4f} ({r_h2_peretyn_z*100:.2f}%)")
        print(f"  R (без пробілів) = {r_h2_peretyn_bez:.4f} ({r_h2_peretyn_bez*100:.2f}%)")
        
        print(f"\nМодель H2 (без перетину):")
        print(f"  R (з пробілами) = {r_h2_bez_peretyn_z:.4f} ({r_h2_bez_peretyn_z*100:.2f}%)")
        print(f"  R (без пробілів) = {r_h2_bez_peretyn_bez:.4f} ({r_h2_bez_peretyn_bez*100:.2f}%)")
    
    finally:
        output_handler.close()
        sys.stdout = output_handler.terminal


if __name__ == "__main__":
    main()