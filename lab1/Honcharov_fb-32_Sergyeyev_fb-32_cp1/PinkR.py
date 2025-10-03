import math

alphabet_with_space = 'абвгдежзийклмнопрстуфхцчшщыьэюя '

def calculate_redundancy(H_inf, H0):
    return 1 - (H_inf / H0)

h10 = (3.196 + 3.555) / 2 
h20 = (1.934 + 2.78) / 2 
h30 = (1.798 + 2.52) / 2 

h0 = math.log2(len(alphabet_with_space))
r_h10 = calculate_redundancy(h10, h0)
r_h20 = calculate_redundancy(h20, h0)
r_h30 = calculate_redundancy(h30, h0)

print("\n--- Значення надлишковості ---")
print(f"R для H10: {r_h10:.5f}")
print(f"R для H20: {r_h20:.5f}")
print(f"R для H30: {r_h30:.5f}")