import matplotlib.pyplot as plt

r_values = list(range(2, 31)) 
ic_cipher = [
    0.047138, 0.041104, 0.038781, 0.039616, 0.036713,
    0.034248, 0.035649, 0.037317, 0.034159, 0.035603,
    0.034373, 0.034095, 0.033662, 0.033298, 0.034536,
    0.033667, 0.034159, 0.035508, 0.034479, 0.034683,
    0.033901, 0.033524, 0.034123, 0.035061, 0.033118,
    0.033930, 0.035493, 0.033414, 0.033948
]
ic_theoretical = 0.055839
ic_plaintext = 0.054606

fig, ax = plt.subplots(figsize=(10, 6))

ax.plot(r_values, ic_cipher, color='blue', linestyle='-', linewidth=2, marker='')
ax.axhline(y=ic_theoretical, color='red', linestyle='--', linewidth=1.5, label='Теоретичний IC')
ax.axhline(y=ic_plaintext, color='green', linestyle='--', linewidth=1.5, label='IC відкритого тексту')

ax.grid(True, which='major', axis='y', linestyle='-', color='gray', alpha=0.5)
ax.grid(False, which='major', axis='x')  

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(True)
ax.spines['bottom'].set_visible(True)

ax.set_xlabel('Довжина ключа r', fontsize=12)
ax.set_ylabel('Індекс відповідності I(r)', fontsize=12)
ax.set_xlim(2, 30)
ax.set_ylim(0.03, 0.06) 

ax.legend(loc='upper right', fontsize=10)
ax.set_title('Залежність індексу відповідності від довжини ключа', fontsize=14, pad=20)

plt.savefig('ic_vs_r_diagram.png', dpi=300, bbox_inches='tight')
plt.show()
