import math

data = {
    10: (2.31062508101796, 3.11332989948939),
    20: (1.9167458982552, 2.59530861634623),
    35: (1.48100572462754, 2.13339581375916)
}

m = 32
log_m = math.log2(m)

print("Надлишковість R для різних кількостей символів:\n")
for N, (H_min, H_max) in data.items():
    R_min = 1 - H_max / log_m 
    R_max = 1 - H_min / log_m 
    print(f"Для {N} символів:")
    print(f"  R_min = {R_min:.6f}")
    print(f"  R_max = {R_max:.6f}\n")

